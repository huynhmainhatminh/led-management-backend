from typing import Optional

from app.core.exceptions import AppError
from app.modules.projects.schemas import (
    PROJECT_ORDER_STATUS_LABELS,
    ProjectOrderCreate,
    ProjectOrderStatus,
)


class ProjectOrderService:
    def __init__(self, orders_repo, components_repo):
        self.repo = orders_repo
        self.components_repo = components_repo

    def _get_or_404(self, order_id: int) -> dict:
        order = self.repo.get(order_id)
        if not order:
            raise AppError(404, "PROJECT_ORDER_NOT_FOUND", f"Không tìm thấy đơn hàng id={order_id}")
        return order

    def _with_status_label(self, order: dict) -> dict:
        return {**order, "statusLabel": PROJECT_ORDER_STATUS_LABELS[ProjectOrderStatus(order["status"])]}

    def list_orders(self, page: int = 0, size: int = 10, status: Optional[ProjectOrderStatus] = None) -> dict:
        orders = self.repo.all()
        if status is not None:
            orders = [order for order in orders if order["status"] == status.value]
        orders.sort(key=lambda order: order["id"], reverse=True)
        start = page * size
        return {
            "content": [self._with_status_label(order) for order in orders[start:start + size]],
            "page": page,
            "size": size,
            "totalElements": len(orders),
            "totalPages": (len(orders) + size - 1) // size,
        }

    def get_order(self, order_id: int) -> dict:
        return self._with_status_label(self._get_or_404(order_id))

    def create_order(self, body: ProjectOrderCreate) -> dict:
        with self.repo.lock:
            # Reject repeated component IDs so every line and subtotal is unambiguous.
            component_ids = [item.componentId for item in body.items]
            if len(component_ids) != len(set(component_ids)):
                raise AppError(400, "DUPLICATE_COMPONENT", "Mỗi linh kiện chỉ được xuất hiện một lần trong đơn hàng")

            lines = []
            total_amount = 0
            for requested in body.items:
                component = self.components_repo.get(requested.componentId)
                if not component:
                    raise AppError(404, "COMPONENT_NOT_FOUND", f"Không tìm thấy linh kiện id={requested.componentId}")
                if component.get("status") != "ACTIVE":
                    raise AppError(400, "COMPONENT_INACTIVE", f"Linh kiện '{component['code']}' đã ngừng sử dụng")

                unit_price = component["unitPrice"]
                subtotal = unit_price * requested.quantity
                total_amount += subtotal
                lines.append({
                    "componentId": component["id"],
                    "code": component["code"],
                    "name": component["name"],
                    "unit": component["unit"],
                    "unitPrice": unit_price,
                    "quantity": requested.quantity,
                    "subtotal": subtotal,
                })

            record = self.repo.insert({
                **body.model_dump(exclude={"items"}),
                "items": lines,
                "totalAmount": total_amount,
                "currency": "VND",
                "status": ProjectOrderStatus.PREPARING.value,
            })
        return self._with_status_label(record)

    def update_status(self, order_id: int, status: ProjectOrderStatus) -> dict:
        with self.repo.lock:
            self._get_or_404(order_id)
            updated = self.repo.update(order_id, {"status": status.value})
        return self._with_status_label(updated)

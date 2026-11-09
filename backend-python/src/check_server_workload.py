import argparse
from getpass import getpass
from uuid import UUID, uuid4

from sqlalchemy import delete, select

from src.create_app import create_app
from src.infrastructure.models import NodeModel, WorkloadModel


def check_constraint(server_id: str, expected_code: str) -> None:
    server_id = str(UUID(server_id))

    if not expected_code.startswith("PY-SRV-"):
        raise RuntimeError("Chỉ kiểm tra trên Server thử nghiệm PY-SRV-.")

    app = create_app()
    database = app.extensions["database"]

    workload_id = str(uuid4())
    fixture_created = False

    try:
        with app.test_client() as client:
            login_response = client.post(
                "/auth/login",
                json={
                    "email": "admin@arimms.local",
                    "password": getpass("Mật khẩu admin: "),
                },
            )

            login_data = login_response.get_json()

            if (
                login_response.status_code != 200
                or not isinstance(login_data, dict)
                or login_data.get("role") != "Administrator"
            ):
                raise RuntimeError("Đăng nhập Admin không thành công.")

            token = login_data.get("accessToken")

            if not token:
                raise RuntimeError("Không nhận được access token.")

            with database.create_session() as session:
                server = session.get(NodeModel, server_id)

                if server is None or server.code != expected_code:
                    raise RuntimeError(
                        "Server không tồn tại hoặc mã không khớp."
                    )

                existing_workload = session.execute(
                    select(WorkloadModel.id)
                    .where(WorkloadModel.node_id == server_id)
                    .limit(1)
                ).scalar_one_or_none()

                if existing_workload is not None:
                    raise RuntimeError(
                        "Cần dùng Server thử nghiệm chưa có Workload."
                    )

                session.add(
                    WorkloadModel(
                        id=workload_id,
                        node_id=server_id,
                        code=f"PY-WL-{uuid4().hex[:8]}",
                        name="Workload kiểm thử ràng buộc xóa",
                        runtime_id=None,
                    )
                )

                session.commit()
                fixture_created = True

            response = client.delete(
                f"/servers/{server_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )

            print(f"DELETE Server còn Workload: {response.status_code}")

            if response.status_code != 409:
                raise RuntimeError(
                    "Kết quả không đúng: phải trả về 409."
                )

            with database.create_session() as session:
                server = session.get(NodeModel, server_id)
                workload = session.get(WorkloadModel, workload_id)

                if server is None or workload is None:
                    raise RuntimeError(
                        "Server hoặc Workload đã bị mất."
                    )

                if workload.node_id != server_id:
                    raise RuntimeError("Quan hệ Workload bị thay đổi.")

            print("Server và Workload được giữ nguyên: OK")

    finally:
        try:
            if fixture_created:
                with database.create_session() as session:
                    session.execute(
                        delete(WorkloadModel).where(
                            WorkloadModel.id == workload_id,
                            WorkloadModel.node_id == server_id,
                        )
                    )
                    session.commit()

                print("Đã dọn Workload thử nghiệm.")
        finally:
            database.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--expected-code", required=True)
    arguments = parser.parse_args()

    check_constraint(
        arguments.server_id,
        arguments.expected_code,
    )
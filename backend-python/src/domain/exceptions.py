class AuthenticationError(Exception):
    """Thông tin đăng nhập hoặc tài khoản không hợp lệ."""


class ValidationError(Exception):
    """Dữ liệu đầu vào không hợp lệ."""


class ResourceNotFoundError(Exception):
    """Không tìm thấy tài nguyên."""


class ResourceConflictError(Exception):
    """Xung đột dữ liệu hoặc ràng buộc quan hệ."""
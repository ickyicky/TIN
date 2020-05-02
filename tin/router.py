from .server.router import Router
from .views.file import FilePost, FileGet, MakeDir, ListDir
from .views.auth import authorize

router = Router()
router.register(("POST", r"/file/(?P<file_path>[\/A-Za-z0-9\.]+)", FilePost))
router.register(("GET", r"/file/(?P<file_path>[\/A-Za-z0-9\.]+)", FileGet))
router.register(("POST", r"/dir/(?P<dir_path>[\/A-Za-z0-9\.]+)", MakeDir))
router.register(("GET", r"/dir/(?P<dir_path>[\/A-Za-z0-9\.]+)", ListDir))
router.register(("GET", r"/dir", ListDir))
router.register(("POST", r"/authorize", authorize))

from .server.router import Router
from .views.file import FilePost, FileGet, FileDelete, MakeDir, ListDir, DeleteDir
from .views.auth import authorize

router = Router()
router.register(("POST", r"/file/(?P<file_path>[\/A-Za-z0-9\.\_]+)", FilePost))
router.register(("GET", r"/file/(?P<file_path>[\/A-Za-z0-9\.\_]+)", FileGet))
router.register(("DELETE", r"/file/(?P<file_path>[\/A-Za-z0-9\.\_]+)", FileDelete))
router.register(("POST", r"/dir/(?P<dir_path>[\/A-Za-z0-9\.\_]+)", MakeDir))
router.register(("GET", r"/dir/(?P<dir_path>[\/A-Za-z0-9\.\_]+)", ListDir))
router.register(("DELETE", r"/dir/(?P<dir_path>[\/A-Za-z0-9\.\_]+)", DeleteDir))
router.register(("GET", r"/dir", ListDir))
router.register(("POST", r"/authorize", authorize))

from .server.router import Router
from .views.file import FilePost, FileGet, FileDelete, MakeDir, ListDir, DeleteDir
from .views.auth import authorize, prolong_session, change_password
from .views import users

router = Router()
router.register(("POST", r"/file/(?P<file_path>[\/A-Za-z0-9\.\_]+)", FilePost))
router.register(("GET", r"/file/(?P<file_path>[\/A-Za-z0-9\.\_]+)", FileGet))
router.register(("DELETE", r"/file/(?P<file_path>[\/A-Za-z0-9\.\_]+)", FileDelete))

router.register(("POST", r"/dir/(?P<dir_path>[\/A-Za-z0-9\_]+)", MakeDir))
router.register(("GET", r"/dir/(?P<dir_path>[\/A-Za-z0-9\_]+)", ListDir))
router.register(("DELETE", r"/dir/(?P<dir_path>[\/A-Za-z0-9\_]+)", DeleteDir))
router.register(("GET", r"/dir", ListDir))

router.register(("POST", r"/authorize", authorize))
router.register(("POST", r"/prolong-session", prolong_session))
router.register(("POST", r"/change-password", change_password))

router.register(("PATCH", r"/users/(?P<user_id>[0-9]+)", users.modify))
router.register(("DELETE", r"/users/(?P<user_id>[0-9]+)", users.delete))
router.register(("GET", r"/users", users.get))
router.register(("POST", r"/users", users.create))

router.register(("POST", r"/produce-exception", lambda x: int("ASD") - x))

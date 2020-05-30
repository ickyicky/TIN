from .server.parsers import HTTPParser
from .server.handler import HTTPHandler
from .server.worker import SocketListener
from .server.middleware.AuthGuardian import AuthGuardian
from .server.middleware.DatabaseMiddleware import DatabaseMiddleware
from .server.middleware.HTTPHeaders import HTTPHeaders
from .router import router
from .auth.Auth import Authorization
from . import domain
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import logging
import ssl
import argparse
import time
import sys
import json


LOG_FORMAT = "%(asctime)s.%(msecs)03d %(process)s.%(thread)s %(levelname)7s: %(name)s %(message)s"


def setup_database(dbssn):
    domain.metadata.create_all(bind=dbssn.get_bind())


def get_dbssn(config, echo=False):
    db_uri = config["db_uri"]

    engine = create_engine(db_uri, echo=echo, pool_size=20, max_overflow=10)
    Session = scoped_session(
        sessionmaker(autoflush=True, autocommit=False, bind=engine)
    )
    dbssn = Session
    try:
        engine.connect()
        return dbssn
    except:
        logging.error("Could not connect to database")
        time.sleep(1)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--ssl", help="SSL", action="store_true")
    parser.add_argument("-c", "--config", help="Config file", action="store")
    parser.add_argument(
        "-i", "--init-database", help="Initialize database tables", action="store_true"
    )
    parser.add_argument("--add-superuser", help="Add superuser", action="store_true")
    parser.add_argument("--start", help="Start server", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

    with open(args.config) as f:
        config = json.load(f)

    dbssn_factory = get_dbssn(config, echo=True)
    dbssn = dbssn_factory()

    if args.init_database:
        setup_database(dbssn)

    if args.add_superuser:
        superuser = domain.User()
        superuser.username = "superuser"
        superuser.first_name = "Super"
        superuser.last_name = "User"
        superuser.password_set("AdMiNiStRaToR1@3")
        dbssn.add(superuser)
        dbssn.commit()

    if not args.start:
        sys.exit(0)

    if args.ssl:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

        server_cert = config["server_cert"]
        server_key = config["server_key"]

        context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    else:
        context = None

    auth_module = Authorization(user_model=domain.User, secret=config["secret"])
    middleware = [
        HTTPHeaders(cdtime=60, keep_alive=True),
        DatabaseMiddleware(dbssn_factory=dbssn_factory),
        AuthGuardian(auth_module),
    ]
    h = HTTPHandler(HTTPParser(), router=router, middleware=middleware)
    server = SocketListener(h, address="0.0.0.0", port=12345, ssl_context=context)
    dbssn.close()
    server.serve()

from pymongo.collection import Collection

from app.projects import bp
from app import db
col: Collection = db['projectTB']
@bp.route('/')
def index():
    return "This is The Project Main Route"
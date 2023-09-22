from app.projects import bp

@bp.route('/')
def index():
    return "This is The Project Main Route"
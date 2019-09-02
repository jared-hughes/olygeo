from ..parser import *
from ..render import SVG
from ..solver import *

def problem_to_spec(problem):
    """
    parse
    rearrange AST to variables, constraints, draw commands
    that is the spec

    Parameters
    ----------
    Sentences as a single string

    Returns
    --------
    {
        param_objects: [...],
        constraints: [...],
        drawn: [...]
    }
    """
    tokens = lex_string(problem)
    print("tokens", tokens)
    result = parse(tokens)
    ast = result.value
    print("ast")
    ast.pprint()
    spec = ast.get_spec()
    return spec

def spec_to_pp(spec):
    """
    take a spec and de-jsonify it (almost eval-worthy)

    Parameters
    ----------
    spec from :func:`problem_to_spec`

    Returns
    --------
    '''
    Variable
    Constraint
    Drawn
    '''
    """
    return 2

def spec_to_solution(spec):
    """
    Parameters
    ----------
    spec from :func:`problem_to_spec`

    Returns
    --------
    {
        param_objects: [...], # with values
        drawn: [...]
    }
    """
    return 3

def solution_to_svg(solution):
    """
    Parameters
    ----------
    solution from :func:`spec_to_solution`

    Returns
    --------
    svg man
    """
    return 4

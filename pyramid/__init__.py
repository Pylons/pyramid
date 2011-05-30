from pyramid.request import Request
from pyramid.response import Response
Response.RequestClass = Request
Request.ResponseClass = Response
del Request, Response

# KnotTheory

# Restrictions of Image
 - Can't have different arcs touching eachother

# Ideas
 - Maybe not necessary to do BFS on all pixels of an arc? Just find the boundary?
 - Could do that by BFSing the background, going one pixel in on the found arcs, and those are are the boundary points
 - For links, the knots might be different colors. Add component functionality
 - 3D seifert surfaces plots using matplotlib
 - http://hmeine.github.io/qimage2ndarray/ instead of files
 - separating spheres
 - generate a knot given crossing index
 

## To Connect Endpoints
 - check distance from the endpoints and the intersection (intersection should be relatively equadistant between endpoints)
 - try all orientations of all arcs in any order ... this would get you all potential orderings... which are just all of them lmao
 - check to make sure endpoints cross over (close to perpendicular) to another rope
 - just go down a rope and check all sides of it for endpoints of other ropes (directionality would still be better)
 - when using first derivative to get slope, get as close as you can do perpendicular against the end boundary of the line
 - intersection likely to be near another line

## Credit:
# StackOverflow
 - 
# see https://www.createspace.com/Products/Book/#content4
# https://www.createspace.com/Help/Index.jsp?orgId=00D300000001Sh9&id=50170000000I7be

page_count = 600
bleed = .125
spine_width = .002252 * page_count
trim_width = 7.5
trim_height = 9.25
min_cover_width = bleed + trim_width + spine_width + trim_width + bleed
min_cover_height = bleed + trim_height + bleed

print "spine width ", spine_width, "inches"
print "min cover width ", min_cover_width, "inches"
print "min cover height ", min_cover_height, "inches"

print "barcode placeholder width: 2 inches"
print "barcode placeholder height: 1.2 inches"
print "bottom of barcode must be .25 inches from bottom trim line of cover"
print "right side of barcode must be .25 inches to left of spine"

# imports
import pygame as pg
import math   as m

# options
_fps = 60
_screen_size = (1920, 1080)
_center = (_screen_size[0]//2, _screen_size[1]//2)

_vector_mass = 1
_gravity = 40 * _vector_mass

_spring_stiffness = 250
_rest_length = 20
_damp_factor = 0.7

_pressure = 10000

# rendering options
_background_color = (25, 25, 25)

_rect_color1 = (255, 255, 255)
_rect_color2 = (175, 175, 175)

_drawing_rect_color1 = (100, 100, 100)
_drawing_rect_color2 = (50, 50, 50)

_text_color = (255, 255, 255)

_draw_points = True
_draw_springs = True

_point_color1 = (255, 0, 0)
_point_color2 = (200, 0, 0)
_spring_color = (0, 0, 0)

# circle options
_circle_radius = 100
_circle_points = 20

# functions
def magnitude(p):
    return m.sqrt((p[0] * p[0]) + (p[1] * p[1]))

def normalize(p):
    return (p[0]/magnitude(p), p[1]/magnitude(p))

def dot(pa, pb):
    return pa[0] * pb[0] + pa[1] * pb[1]

def vector_difference(pa, pb):
    return (pa[0]-pb[0], pa[1]-pb[1])

def vector_multiply(p, n):
    return (p[0]*n, p[1]*n)

def calculate_area(points):
    area = 0
    for i, point in enumerate(points):
        if i+1 == len(points):
            area += (point[0][0] * points[0][0][1] - points[0][0][0] * point[0][1])
        else:
            area += (point[0][0] * points[i+1][0][1] - points[i+1][0][0] * point[0][1])
    return 0.5 * abs(area)

def build_circle(radius, points, center):
    spacing = (m.pi * 2) / points
    positions = []
    for point in range(points):
        angle = spacing * point
        x = center[0] + (radius * m.cos(angle))
        y = center[1] + (radius * m.sin(angle))
        positions.append(([x, y], [0, 0], [0, 0], _vector_mass, [0, 0]))
    return positions

def create_rect(start, end):
    if start[0] < end[0]:
        if start[1] < end[1]:
            return (start[0], start[1], end[0]-start[0], end[1]-start[1])
        else:
            return (start[0], end[1], end[0]-start[0], start[1]-end[1])
    else:
        if start[1] < end[1]:
            return (end[0], start[1], start[0]-end[0], end[1]-start[1])
        else:
            return (end[0], end[1], start[0]-end[0], start[1]-end[1])

# initialize pygame
pg.init()
win = pg.display.set_mode(_screen_size, pg.FULLSCREEN|pg.DOUBLEBUF)
pg.display.set_caption("Gpopcorn's Softbody Engine")
clk = pg.time.Clock()

font = pg.font.Font('freesansbold.ttf', 20)

# create shape
circle  = build_circle(_circle_radius, _circle_points, (960, 50))
springs = []
for i, point in enumerate(circle):
    if i+1 == len(circle):
        springs.append((i, 0))
    else:
        springs.append((i, i+1))

# create environment
rects = [(0, 1000, 1920, 50)]

drag = [0, 0]
is_drag = False

run = True
pause = True
while run:
    # get delta time
    delta = clk.tick(_fps) / 400
    
    # events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                pause = not pause
                
        # environment building
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                drag = pg.mouse.get_pos()
                is_drag = True
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                rects.append(create_rect(drag, pg.mouse.get_pos()))
                is_drag = False
            
    # create background effect
    win.fill(_background_color)
    for i in range(20):
        pg.draw.circle(win, (_background_color[0]+i, _background_color[1]+i, _background_color[2]+i), _center, 1000-(i*50))
    
    if is_drag == True:
        pg.draw.rect(win, _drawing_rect_color1, create_rect(drag, pg.mouse.get_pos()))
        pg.draw.rect(win, _drawing_rect_color2, create_rect(drag, pg.mouse.get_pos()), 5)
    
    # draw environment
    for rect in rects:
        pg.draw.rect(win, _rect_color1, rect)
        pg.draw.rect(win, _rect_color2, rect, 5)
    
    # calculate circle area for IGL
    circle_area = calculate_area(circle)
    
    # everything else
    for spring in springs:
        if pause == False:
            distance = magnitude(vector_difference(circle[spring[0]][0],circle[spring[1]][0]))
            spring_force = _spring_stiffness * (distance - _rest_length)
            direction = normalize(vector_difference(circle[spring[0]][0], circle[spring[1]][0]))
            vel_difference = vector_difference(circle[spring[0]][1], circle[spring[1]][1])
            total_force = dot(direction, vel_difference) * _damp_factor + spring_force

            normal = ((circle[spring[1]][0][1] - circle[spring[0]][0][1]), -(circle[spring[1]][0][0] - circle[spring[0]][0][0]))
            
            circle[spring[0]][4][0] += ((_pressure * distance) / circle_area) * normal[0]
            circle[spring[0]][4][1] += ((_pressure * distance) / circle_area) * normal[1]
            circle[spring[1]][4][0] += ((_pressure * distance) / circle_area) * normal[0]
            circle[spring[1]][4][1] += ((_pressure * distance) / circle_area) * normal[1]

            circle[spring[0]][4][0] += vector_multiply(normalize(vector_difference(circle[spring[1]][0], circle[spring[0]][0])), total_force)[0]
            circle[spring[0]][4][1] += vector_multiply(normalize(vector_difference(circle[spring[1]][0], circle[spring[0]][0])), total_force)[1]
            circle[spring[1]][4][0] += vector_multiply(direction, total_force)[0]
            circle[spring[1]][4][1] += vector_multiply(direction, total_force)[1]
        
        # draw the springs
        if _draw_springs == True:
            pg.draw.line(win, _spring_color, circle[spring[0]][0], circle[spring[1]][0], 4)
    
    for point in circle:
        if pause == False:
            point[2][0], point[2][1] = 0, 0 # reset force
            point[2][0] = point[4][0] # add spring force and IGL
            point[2][1] = _gravity + point[4][1] # add gravity and spring force and IGL
            
            # reset spring forces
            point[4][0], point[4][1] = 0, 0
            
            # add force to velocity
            point[1][0] += (point[2][0] * delta) / _vector_mass
            point[1][1] += (point[2][1] * delta) / _vector_mass
            
            # add velocity to position
            point[0][0] += point[1][0] * delta
            point[0][1] += point[1][1] * delta
            
            # collision
            for rect in rects:
                if point[0][0] > rect[0] and point[0][0] < rect[0] + rect[2]:
                    if point[0][1] > rect[1] and point[0][1] < rect[1] + rect[3]:
                        # get point distance from each wall
                        col_lef = point[0][0] - rect[0]
                        col_rig = (rect[0] + rect[2]) - point[0][0]
                        col_top = point[0][1] - rect[1]
                        col_bot = (rect[1] + rect[3]) - point[0][1]
                        
                        # change position
                        smallest_col = min(col_lef, col_rig, col_top, col_bot)
                        if smallest_col == col_lef:
                            point[0][0] = rect[0]
                            point[1][0] = 0
                        elif smallest_col == col_rig:
                            point[0][0] = rect[0] + rect[2]
                            point[1][0] = 0
                        elif smallest_col == col_top:
                            point[0][1] = rect[1]
                            point[1][1] = 0
                        elif smallest_col == col_bot:
                            point[0][1] = rect[1] + rect[3]
                            point[1][1] = 0
        
        # draw the point
        if _draw_points == True:
            pg.draw.circle(win, _point_color1, point[0], 5)
            pg.draw.circle(win, _point_color2, point[0], 3)
            
    fps_counter = font.render(f'FPS: {round(clk.get_fps())}', True, _text_color)
    win.blit(fps_counter, (0, 0))
    if pause == True:
        paused = font.render('PAUSED', True, _text_color)
        win.blit(paused, (0, 25))
            
    # refresh
    pg.display.flip()

# quit
pg.quit()
quit()
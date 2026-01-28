import pygame

class Rasterizer:
    @staticmethod
    def scanline_fill(surface, vertices, color):
        if len(vertices) < 3: return

        width, height = surface.get_size()
        ys = [v.y for v in vertices]
        y_min = max(0, int(min(ys)))
        y_max = min(height - 1, int(max(ys)))

        with pygame.PixelArray(surface) as pixels:
            raw_color = surface.map_rgb(color)
            
            for y in range(y_min, y_max + 1):
                intersections = []
                for i in range(len(vertices)):
                    v1, v2 = vertices[i], vertices[(i + 1) % len(vertices)]
                    if int(v1.y) == int(v2.y): continue
                    
                    p1, p2 = (v1, v2) if v1.y < v2.y else (v2, v1)
                    if p1.y <= y < p2.y:
                        x = p1.x + (y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y)
                        intersections.append(x)

                intersections.sort()

                for i in range(0, len(intersections), 2):
                    if i + 1 < len(intersections):
                        x_start = max(0, int(intersections[i]))
                        x_end = min(width - 1, int(intersections[i+1]))
                        
                        if x_start < x_end:
                            pixels[x_start : x_end + 1, y] = raw_color

    @staticmethod
    def scanline_texture(surface, vertices, texture):
        if len(vertices) < 3: return
        
        width, height = surface.get_size()
        tex_w, tex_h = texture.get_size()
        
        ys = [v.y for v in vertices]
        y_min = max(0, int(min(ys)))
        y_max = min(height - 1, int(max(ys)))
        
        with pygame.PixelArray(surface) as pixels, pygame.PixelArray(texture) as tex_pixels:
            for y in range(y_min, y_max + 1):
                inter = []
                for i in range(len(vertices)):
                    v1, v2 = vertices[i], vertices[(i + 1) % len(vertices)]
                    if int(v1.y) == int(v2.y): continue
                    
                    p1, p2 = (v1, v2) if v1.y < v2.y else (v2, v1)
                    if p1.y <= y < p2.y:
                        factor = (y - p1.y) / (p2.y - p1.y)
                        x = p1.x + factor * (p2.x - p1.x)
                        u = p1.u + factor * (p2.u - p1.u)
                        v = p1.v + factor * (p2.v - p1.v)
                        inter.append((x, u, v))

                inter.sort(key=lambda item: item[0])

                for i in range(0, len(inter), 2):
                    if i + 1 >= len(inter): continue
                    
                    xa, ua, va = inter[i]
                    xb, ub, vb = inter[i+1]
                    
                    x_start, x_end = int(xa), int(xb)
                    x_clamped_start = max(0, x_start)
                    x_clamped_end = min(width - 1, x_end)
                    
                    seg_w = x_end - x_start
                    if seg_w <= 0: continue

                    inv_w = 1.0 / seg_w
                    du = (ub - ua) * inv_w
                    dv = (vb - va) * inv_w
                    
                    offset = x_clamped_start - x_start
                    curr_u = ua + offset * du
                    curr_v = va + offset * dv

                    for x in range(x_clamped_start, x_clamped_end + 1):
                        tx = int(curr_u * (tex_w - 1)) % tex_w
                        ty = int(curr_v * (tex_h - 1)) % tex_h
                        pixels[x, y] = tex_pixels[tx, ty]
                        curr_u += du
                        curr_v += dv
    
    @staticmethod
    def interpola_cor(color1, color2, factor):
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        return (r, g, b)

    @staticmethod
    def scanline_fill_gradiente(surface, vertices, color_top, color_bottom):
        if len(vertices) < 3: return

        width, height = surface.get_size()
        ys = [v.y for v in vertices]
        y_min = max(0, int(min(ys)))
        y_max = min(height - 1, int(max(ys)))
        
        poly_height = y_max - y_min
        if poly_height == 0: poly_height = 1

        with pygame.PixelArray(surface) as pixels:
            for y in range(y_min, y_max + 1):
                factor = (y - y_min) / poly_height
                current_color = Rasterizer.interpola_cor(color_top, color_bottom, factor)
                raw_color = surface.map_rgb(current_color)
                
                intersections = []
                for i in range(len(vertices)):
                    v1, v2 = vertices[i], vertices[(i + 1) % len(vertices)]
                    if int(v1.y) == int(v2.y): continue
                    p1, p2 = (v1, v2) if v1.y < v2.y else (v2, v1)
                    if p1.y <= y < p2.y:
                        x = p1.x + (y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y)
                        intersections.append(x)

                intersections.sort()

                for i in range(0, len(intersections), 2):
                    if i + 1 < len(intersections):
                        x_start = max(0, int(intersections[i]))
                        x_end = min(width - 1, int(intersections[i+1]))
                        if x_start < x_end:
                            pixels[x_start : x_end + 1, y] = raw_color
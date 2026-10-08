"""GLSL 4.3 del motor. Luz en unidades HDR lineales; el tonemap (ACES) va al final."""

VERT_MALLA = """
#version 430
uniform mat4 M; uniform mat4 V; uniform mat4 P;
in vec3 in_pos; in vec3 in_nrm; in vec2 in_uv;
in vec3 in_alb; in float in_met; in float in_rug; in float in_tipo;
out vec3 vW; out vec3 vN; out vec2 vUV; out vec3 vAlb; out vec3 vMat; out vec3 vObj;
void main(){
  vec4 w = M * vec4(in_pos, 1.0);
  vW = w.xyz; vN = mat3(M) * in_nrm; vUV = in_uv; vAlb = in_alb; vObj = in_pos;
  vMat = vec3(in_met, in_rug, in_tipo);
  gl_Position = P * V * w;
}
"""

VERT_TIERRA = """
#version 430
uniform mat4 M; uniform mat4 V; uniform mat4 P;
in vec3 in_pos; in vec3 in_nrm; in vec2 in_uv;
out vec3 vW; out vec3 vN; out vec2 vUV;
void main(){
  vec4 w = M * vec4(in_pos, 1.0);
  vW = w.xyz; vN = mat3(M) * in_nrm; vUV = in_uv;
  gl_Position = P * V * w;
}
"""

FRAG_TIERRA = """
#version 430
uniform sampler2D tdia; uniform sampler2D tnoche; uniform sampler2D tnubes;
uniform vec3 sol; uniform vec3 cam; uniform float sol_i; uniform float noche_i; uniform float nubes_du;
in vec3 vW; in vec3 vN; in vec2 vUV;
out vec4 f;
void main(){
  vec3 N = normalize(vN); vec3 V = normalize(cam - vW); vec3 L = sol;
  float ndl = dot(N, L);
  vec3 dia = pow(texture(tdia, vUV).rgb, vec3(2.2));
  vec3 noc = pow(texture(tnoche, vUV).rgb, vec3(2.2));
  float nub = texture(tnubes, vUV + vec2(nubes_du, 0.0)).r;
  nub = smoothstep(0.15, 0.9, nub);
  float lam = max(ndl, 0.0);
  float crep = smoothstep(-0.12, 0.18, ndl);                 // crepúsculo
  float oc = clamp((dia.b - max(dia.r, dia.g) * 1.05) * 30.0, 0.0, 1.0);
  vec3 sup = mix(dia, vec3(0.92), nub * 0.92);
  vec3 H = normalize(L + V);
  float spec = pow(max(dot(N, H), 0.0), 90.0) * oc * (1.0 - nub) * 2.5;
  float spec2 = pow(max(dot(N, H), 0.0), 12.0) * oc * (1.0 - nub) * 0.12;
  // enrojecimiento cerca del terminador (camino largo por la atmósfera)
  vec3 tinte = mix(vec3(1.0, 0.45, 0.25), vec3(1.0), smoothstep(0.0, 0.35, ndl));
  vec3 col = sup * lam * tinte * sol_i + (spec + spec2) * lam * sol_i * vec3(1.0, 0.95, 0.85);
  float lum = dot(noc, vec3(0.3, 0.5, 0.2));
  vec3 luces = vec3(1.0, 0.72, 0.42) * pow(max(lum - 0.02, 0.0), 1.4) * 3.0;
  col += luces * (1.0 - crep) * (1.0 - nub * 0.75) * noche_i;
  col += noc * 0.015 * (1.0 - crep);                         // relieve tenue del lado nocturno
  f = vec4(col, 1.0);
}
"""

# Dispersión simple Rayleigh + Mie a lo largo del rayo de vista (cáscara dibujada por la cara trasera).
FRAG_ATMOSFERA = """
#version 430
uniform vec3 cam; uniform vec3 sol; uniform float sol_i;
uniform float Ra; uniform float Hr; uniform float Hm;
uniform vec3 bR; uniform float bM;
in vec3 vW; in vec3 vN; in vec2 vUV;
out vec4 f;
vec2 esfera(vec3 o, vec3 d, float r){
  float b = dot(o, d); float c = dot(o, o) - r * r; float h = b * b - c;
  if (h < 0.0) return vec2(1e9, -1e9);
  h = sqrt(h); return vec2(-b - h, -b + h);
}
vec2 prof_sol(vec3 p){                       // profundidad óptica hacia el Sol (4 muestras)
  vec2 a = esfera(p, sol, Ra);
  if (esfera(p, sol, 1.0).x > 0.0) return vec2(1e3);           // la Tierra tapa el Sol
  float ds = a.y / 4.0; vec2 od = vec2(0.0);
  for (int i = 0; i < 4; i++){
    float h = length(p + sol * ds * (float(i) + 0.5)) - 1.0;
    od += vec2(exp(-h / Hr), exp(-h / Hm)) * ds;
  }
  return od;
}
void main(){
  vec3 d = normalize(vW - cam);
  vec2 a = esfera(cam, d, Ra);
  vec2 t = esfera(cam, d, 1.0);
  float t0 = max(a.x, 0.0);
  float t1 = (t.x > 0.0) ? t.x : a.y;
  if (t1 <= t0) discard;
  const int N = 14;
  float ds = (t1 - t0) / float(N);
  vec3 sumR = vec3(0.0); vec3 sumM = vec3(0.0); vec2 odv = vec2(0.0);
  for (int i = 0; i < N; i++){
    vec3 p = cam + d * (t0 + ds * (float(i) + 0.5));
    float h = length(p) - 1.0;
    vec2 dens = vec2(exp(-h / Hr), exp(-h / Hm)) * ds;
    odv += dens;
    vec2 ods = prof_sol(p);
    vec3 tau = bR * (odv.x + ods.x) + bM * 1.1 * (odv.y + ods.y);
    vec3 tr = exp(-tau);
    sumR += dens.x * tr; sumM += dens.y * tr;
  }
  float mu = dot(d, sol);
  float pR = 3.0 / (16.0 * 3.14159) * (1.0 + mu * mu);
  float g = 0.76;
  float pM = 3.0 / (8.0 * 3.14159) * ((1.0 - g * g) * (1.0 + mu * mu)) / ((2.0 + g * g) * pow(1.0 + g * g - 2.0 * g * mu, 1.5));
  vec3 col = (sumR * bR * pR + sumM * bM * pM) * sol_i;
  vec3 trans = exp(-(bR * odv.x + bM * 1.1 * odv.y));
  f = vec4(col, 1.0 - dot(trans, vec3(0.333)) * 0.0);
}
"""

FRAG_MATERIAL = """
#version 430
uniform vec3 sol; uniform vec3 cam; uniform float sol_i;
uniform vec3 amb; uniform vec3 tierra_dir; uniform vec3 tierra_luz;
in vec3 vW; in vec3 vN; in vec2 vUV; in vec3 vAlb; in vec3 vMat; in vec3 vObj;
out vec4 f;
void main(){
  vec3 N = normalize(vN); vec3 V = normalize(cam - vW);
  if (dot(N, V) < 0.0) N = -N;
  float met = vMat.x, rug = vMat.y; int tipo = int(vMat.z + 0.5);
  vec3 alb = vAlb;
  if (tipo == 1){                                   // celdas solares: rejilla de celdas y buses plateados
    vec2 g = fract(vUV * vec2(2.0, 6.0));
    float borde = step(g.x, 0.035) + step(0.965, g.x) + step(g.y, 0.02) + step(0.98, g.y);
    float dedos = step(fract(vUV.x * 2.0 * 14.0), 0.06);
    alb = mix(alb, vec3(0.75), clamp(borde, 0.0, 1.0) * 0.8 + dedos * 0.15);
    rug = mix(0.18, 0.45, clamp(borde, 0.0, 1.0));
  } else if (tipo == 2){                            // reflectarray: parches de cobre de tamaño variable
    vec2 c = vUV * 18.0; vec2 g = fract(c) - 0.5; vec2 id = floor(c) - 9.0;
    float r = 0.18 + 0.14 * sin(length(id) * 0.9);
    float parche = 1.0 - step(r, max(abs(g.x), abs(g.y)));
    alb = mix(vec3(0.10, 0.11, 0.12), alb, parche); met = mix(0.1, 0.9, parche); rug = mix(0.7, 0.3, parche);
  }
  vec3 L = sol; vec3 H = normalize(L + V);
  float ndl = max(dot(N, L), 0.0);
  float a2 = pow(max(rug, 0.05), 4.0);
  float ndh = max(dot(N, H), 0.0);
  float D = a2 / (3.14159 * pow(ndh * ndh * (a2 - 1.0) + 1.0, 2.0));
  vec3 F0 = mix(vec3(0.04), alb, met);
  vec3 F = F0 + (1.0 - F0) * pow(1.0 - max(dot(H, V), 0.0), 5.0);
  vec3 spec = D * F * 0.25;
  vec3 dif = alb * (1.0 - met) / 3.14159;
  vec3 col = (dif + spec) * ndl * sol_i * 3.14159;
  // luz reflejada por la Tierra (albedo) y ambiente tenue
  float nt = max(dot(N, tierra_dir) * 0.5 + 0.5, 0.0);
  col += alb * tierra_luz * nt * (1.0 - met * 0.5) + alb * amb;
  if (tipo == 3) col = vAlb * 4.0;
  f = vec4(col, 1.0);
}
"""

VERT_PUNTOS = """
#version 430
uniform mat4 V; uniform mat4 P; uniform float escala;
in vec3 in_dir; in float in_b; in vec3 in_col;
out vec3 vCol;
void main(){
  vec4 p = P * vec4(mat3(V) * in_dir * 10.0, 1.0);
  gl_Position = p.xyww;                          // en el infinito
  gl_PointSize = (1.2 + 2.2 * sqrt(in_b)) * escala;
  vCol = in_col * in_b;
}
"""

FRAG_PUNTOS = """
#version 430
uniform float brillo;
in vec3 vCol; out vec4 f;
void main(){
  vec2 c = gl_PointCoord * 2.0 - 1.0; float r2 = dot(c, c);
  if (r2 > 1.0) discard;
  f = vec4(vCol * exp(-r2 * 4.0) * brillo, 1.0);
}
"""

# Destellos/halos con tamaño en pixeles y posición en el mundo (Sol, satélites lejanos, estaciones)
VERT_SPRITE = """
#version 430
uniform mat4 V; uniform mat4 P;
in vec3 in_pos; in float in_tam; in vec3 in_col;
out vec3 vCol;
void main(){
  gl_Position = P * V * vec4(in_pos, 1.0);
  gl_PointSize = in_tam; vCol = in_col;
}
"""

FRAG_SPRITE = """
#version 430
in vec3 vCol; out vec4 f;
void main(){
  vec2 c = gl_PointCoord * 2.0 - 1.0; float r = length(c);
  if (r > 1.0) discard;
  float n = exp(-r * r * 9.0) + 0.25 * exp(-r * 3.5) * (1.0 - r);
  f = vec4(vCol * n, 1.0);
}
"""

# Líneas gruesas en pantalla (órbitas, haces): geometry shader línea -> cuádrico
VERT_LINEA = """
#version 430
uniform mat4 V; uniform mat4 P;
in vec3 in_pos; in vec4 in_col;
out vec4 gCol;
void main(){ gl_Position = P * V * vec4(in_pos, 1.0); gCol = in_col; }
"""

GEOM_LINEA = """
#version 430
layout(lines) in; layout(triangle_strip, max_vertices = 4) out;
uniform vec2 pantalla; uniform float grosor;
in vec4 gCol[]; out vec4 fCol; out float fLado;
void main(){
  vec4 a = gl_in[0].gl_Position, b = gl_in[1].gl_Position;
  if (a.w <= 0.0 || b.w <= 0.0) return;
  vec2 sa = a.xy / a.w * pantalla, sb = b.xy / b.w * pantalla;
  vec2 d = normalize(sb - sa + 1e-6); vec2 n = vec2(-d.y, d.x) * grosor;
  vec2 oa = n / pantalla * a.w, ob = n / pantalla * b.w;
  fCol = gCol[0]; fLado = -1.0; gl_Position = vec4(a.xy - oa, a.zw); EmitVertex();
  fCol = gCol[0]; fLado =  1.0; gl_Position = vec4(a.xy + oa, a.zw); EmitVertex();
  fCol = gCol[1]; fLado = -1.0; gl_Position = vec4(b.xy - ob, b.zw); EmitVertex();
  fCol = gCol[1]; fLado =  1.0; gl_Position = vec4(b.xy + ob, b.zw); EmitVertex();
  EndPrimitive();
}
"""

FRAG_LINEA = """
#version 430
in vec4 fCol; in float fLado; out vec4 f;
void main(){ float a = 1.0 - fLado * fLado; f = vec4(fCol.rgb * fCol.a * a, 1.0); }
"""

# Haz de antena: cono aditivo que se desvanece con la distancia al ápice y hacia el borde
FRAG_HAZ = """
#version 430
uniform vec3 color; uniform vec3 cam; uniform float intensidad;
in vec3 vW; in vec3 vN; in vec2 vUV; out vec4 f;
void main(){
  vec3 V = normalize(cam - vW);
  float borde = pow(1.0 - abs(dot(normalize(vN), V)), 1.5);
  float a = (0.25 + 0.75 * borde) * (1.0 - vUV.y * 0.55);
  f = vec4(color * a * intensidad, 1.0);
}
"""

VERT_PANTALLA = """
#version 430
in vec2 in_pos; out vec2 uv;
void main(){ uv = in_pos * 0.5 + 0.5; gl_Position = vec4(in_pos, 0.0, 1.0); }
"""

FRAG_BRILLO = """
#version 430
uniform sampler2D src; uniform float umbral; in vec2 uv; out vec4 f;
void main(){
  vec3 c = texture(src, uv).rgb; float l = max(c.r, max(c.g, c.b));
  f = vec4(c * max(l - umbral, 0.0) / max(l, 1e-4), 1.0);
}
"""

FRAG_BLUR = """
#version 430
uniform sampler2D src; uniform vec2 dir; in vec2 uv; out vec4 f;
void main(){
  float w[5] = float[](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
  vec3 c = texture(src, uv).rgb * w[0];
  for (int i = 1; i < 5; i++){
    c += texture(src, uv + dir * float(i)).rgb * w[i];
    c += texture(src, uv - dir * float(i)).rgb * w[i];
  }
  f = vec4(c, 1.0);
}
"""

FRAG_FINAL = """
#version 430
uniform sampler2D hdr; uniform sampler2D b1; uniform sampler2D b2; uniform sampler2D b3; uniform sampler2D b4;
uniform float exposicion; uniform float bloom; uniform float vineta; uniform float fundido;
in vec2 uv; out vec4 f;
vec3 aces(vec3 x){ return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }
void main(){
  vec3 c = texture(hdr, uv).rgb;
  vec3 b = texture(b1, uv).rgb * 0.5 + texture(b2, uv).rgb * 0.6 + texture(b3, uv).rgb * 0.8 + texture(b4, uv).rgb * 1.0;
  c = (c + b * bloom) * exposicion;
  c = aces(c);
  vec2 q = uv - 0.5; c *= 1.0 - vineta * dot(q, q) * 1.6;
  c = pow(c, vec3(1.0 / 2.2)) * fundido;
  f = vec4(c, 1.0);
}
"""

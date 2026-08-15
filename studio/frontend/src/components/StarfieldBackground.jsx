import { useEffect, useRef } from 'react';
import { motionAllowed, usePref } from '../prefs.js';

const StarfieldBackground = () => {
  const canvasRef = useRef(null);
  // La preferencia de Configuracion re-monta el efecto: al desactivarla el
  // bucle se cancela de verdad (no basta con dejar de pintar).
  const motion = usePref('motion');

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const isMobile = window.innerWidth < 768;
    const PARTICLE_COUNT = isMobile ? 40 : 85;
    const LINK_DISTANCE = isMobile ? 100 : 145;
    const SPEED = 0.35;

    let particles = [];
    let animId;
    let mouse = { x: -9999, y: -9999 };

    // Esta consola se deja abierta horas vigilando renders: el fondo no puede
    // costar un frame de 60 fps con O(n^2) enlaces + un getComputedStyle cada
    // vez. Se limita a ~30 fps, el acento se relee solo al cambiar de tema, y
    // se pinta un unico fotograma estatico si el sistema pide reducir el
    // movimiento o si se ha apagado el fondo en Configuracion.
    const reduceMotion = !motionAllowed(motion);
    const FRAME_MS = 1000 / 30;
    let lastFrame = 0;

    // Dynamically extract RGB representation of theme's --accent color
    const readAccentRgb = () => {
      try {
        const raw = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
        if (raw.startsWith('#')) {
          const r = parseInt(raw.slice(1, 3), 16);
          const g = parseInt(raw.slice(3, 5), 16);
          const b = parseInt(raw.slice(5, 7), 16);
          return `${r}, ${g}, ${b}`;
        }
      } catch (e) {
        // Fallback
      }
      return '0, 216, 246';
    };
    let accentRgb = readAccentRgb();
    // El tema se aplica como data-theme en <html> (themes.js): observarlo es
    // mas barato que releer el color en cada fotograma.
    const themeObserver = new MutationObserver(() => { accentRgb = readAccentRgb(); });
    themeObserver.observe(document.documentElement, { attributeFilter: ['data-theme'] });

    const resize = () => {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const init = () => {
      resize();
      particles = Array.from({ length: PARTICLE_COUNT }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * SPEED,
        vy: (Math.random() - 0.5) * SPEED,
        r: Math.random() * 1.5 + 0.5,
      }));
    };

    const paint = (advance) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const activeAccent = accentRgb;

      // 1. Update positions
      if (advance) {
        for (const p of particles) {
          p.x += p.vx;
          p.y += p.vy;
          if (p.x < 0 || p.x > canvas.width)  p.vx *= -1;
          if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
        }
      }

      // 2. Draw Links (Batching strokes for better performance)
      ctx.lineWidth = 0.6;
      for (let i = 0; i < particles.length; i++) {
        const p1 = particles[i];
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const distSq = dx * dx + dy * dy;
          const limitSq = LINK_DISTANCE * LINK_DISTANCE;
          
          if (distSq < limitSq) {
            const dist = Math.sqrt(distSq);
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(255,255,255,${0.12 * (1 - dist / LINK_DISTANCE)})`;
            ctx.stroke();
          }
        }

        // Mouse interaction
        const mdx = p1.x - mouse.x;
        const mdy = p1.y - mouse.y;
        const mdistSq = mdx * mdx + mdy * mdy;
        const mLimitSq = 140 * 140;
        
        if (mdistSq < mLimitSq) {
          const mdist = Math.sqrt(mdistSq);
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.strokeStyle = `rgba(${activeAccent},${0.35 * (1 - mdist / 140)})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
          ctx.lineWidth = 0.6; // Reset for standard links
        }
      }

      // 3. Draw Particles
      ctx.fillStyle = `rgba(${activeAccent},0.65)`;
      for (const p of particles) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }

    };

    const loop = (ts) => {
      animId = requestAnimationFrame(loop);
      if (ts - lastFrame < FRAME_MS) return;
      lastFrame = ts;
      paint(true);
    };

    const onMouseMove = (e) => { mouse.x = e.clientX; mouse.y = e.clientY; };
    const onMouseLeave = () => { mouse.x = -9999; mouse.y = -9999; };
    const handleResize = () => { resize(); init(); paint(false); };

    init();
    paint(false);

    window.addEventListener('resize', handleResize);
    if (!reduceMotion) {
      animId = requestAnimationFrame(loop);
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseleave', onMouseLeave);
    }

    return () => {
      cancelAnimationFrame(animId);
      themeObserver.disconnect();
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseleave', onMouseLeave);
    };
  }, [motion]);

  return (
    // -z-10, no z-0: esta capa es OPACA (pinta var(--canvas)) y esta
    // posicionada, asi que con z-0 tapaba cualquier contenido NO posicionado
    // que viniera despues en el arbol — por eso las pestañas
    // Salud/Jobs/Recursos de Admin (un <div> plano, sin .panel) eran
    // invisibles. Con z negativo queda debajo de todo el contenido y encima
    // del fondo del documento.
    <div
      className="pointer-events-none fixed inset-0 -z-10 transition-colors duration-300"
      style={{ background: 'var(--canvas)' }}
    >
      <canvas
        ref={canvasRef}
        style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0.85 }}
      />
    </div>
  );
};

export default StarfieldBackground;

import { useEffect, useRef } from 'react';

const StarfieldBackground = () => {
  const canvasRef = useRef(null);

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

    // Dynamically extract RGB representation of theme's --accent color
    const getAccentRgb = () => {
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

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const activeAccent = getAccentRgb();

      // 1. Update positions
      for (const p of particles) {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width)  p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
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

      animId = requestAnimationFrame(draw);
    };

    const onMouseMove = (e) => { mouse.x = e.clientX; mouse.y = e.clientY; };
    const onMouseLeave = () => { mouse.x = -9999; mouse.y = -9999; };
    const handleResize = () => { resize(); init(); };

    init();
    draw();

    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseleave', onMouseLeave);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseleave', onMouseLeave);
    };
  }, []);

  return (
    <div 
      className="fixed inset-0 pointer-events-none z-0 transition-colors duration-300" 
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

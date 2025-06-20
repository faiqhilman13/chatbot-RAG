import React from 'react';
import Particles from './Particles';
import './ParticleBackground.css';

const ParticleBackground = () => {
  return (
    <div className="particle-background">
      <Particles
        particleColors={['#00ffff', '#c27cb9', '#39ff14']} // Neon blue, purple, green
        particleCount={1000}
        particleSpread={10}
        speed={0.05}
        particleBaseSize={100}
        moveParticlesOnHover={false}
        alphaParticles={true}
        disableRotation={false}
        sizeRandomness={0.8}
        cameraDistance={30}
      />
    </div>
  );
};

export default ParticleBackground; 
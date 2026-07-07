import React, { useEffect, useRef } from 'react';
import lottie from 'lottie-web';

interface LottiePlayerProps {
  animationData: any;
  className?: string;
  loop?: boolean;
}

export const LottiePlayer: React.FC<LottiePlayerProps> = ({
  animationData,
  className = '',
  loop = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const anim = lottie.loadAnimation({
      container: containerRef.current,
      renderer: 'svg',
      loop,
      autoplay: true,
      animationData,
    });

    return () => {
      anim.destroy();
    };
  }, [animationData, loop]);

  return <div ref={containerRef} className={className} />;
};

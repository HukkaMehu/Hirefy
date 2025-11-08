import { Variants } from "framer-motion";

/**
 * Fade in animation
 * Use: variants={fadeIn} initial="initial" animate="animate"
 */
export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { 
    opacity: 1,
    transition: { duration: 0.5, ease: "easeOut" }
  },
  exit: { opacity: 0 }
};

/**
 * Slide up animation
 * Use: variants={slideUp} initial="initial" animate="animate"
 */
export const slideUp: Variants = {
  initial: { 
    opacity: 0, 
    y: 20 
  },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: { 
      duration: 0.4, 
      ease: [0.25, 0.1, 0.25, 1.0] 
    }
  },
  exit: { 
    opacity: 0, 
    y: 20 
  }
};

/**
 * Slide down animation
 * Use: variants={slideDown} initial="initial" animate="animate"
 */
export const slideDown: Variants = {
  initial: { 
    opacity: 0, 
    y: -20 
  },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: { 
      duration: 0.4, 
      ease: [0.25, 0.1, 0.25, 1.0] 
    }
  },
  exit: { 
    opacity: 0, 
    y: -20 
  }
};

/**
 * Scale in animation
 * Use: variants={scaleIn} initial="initial" animate="animate"
 */
export const scaleIn: Variants = {
  initial: { 
    opacity: 0, 
    scale: 0.95 
  },
  animate: { 
    opacity: 1, 
    scale: 1,
    transition: { 
      duration: 0.3, 
      ease: [0.25, 0.1, 0.25, 1.0] 
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.95 
  }
};

/**
 * Slide in from left
 * Use: variants={slideLeft} initial="initial" animate="animate"
 */
export const slideLeft: Variants = {
  initial: { 
    opacity: 0, 
    x: -30 
  },
  animate: { 
    opacity: 1, 
    x: 0,
    transition: { 
      duration: 0.4, 
      ease: "easeOut" 
    }
  },
  exit: { 
    opacity: 0, 
    x: -30 
  }
};

/**
 * Slide in from right
 * Use: variants={slideRight} initial="initial" animate="animate"
 */
export const slideRight: Variants = {
  initial: { 
    opacity: 0, 
    x: 30 
  },
  animate: { 
    opacity: 1, 
    x: 0,
    transition: { 
      duration: 0.4, 
      ease: "easeOut" 
    }
  },
  exit: { 
    opacity: 0, 
    x: 30 
  }
};

/**
 * Stagger container for animating children sequentially
 * Use: variants={staggerChildren} initial="initial" animate="animate"
 * Children should use slideUp, fadeIn, or similar variants
 */
export const staggerChildren: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1
    }
  }
};

/**
 * Stagger container with faster animation
 */
export const staggerChildrenFast: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0
    }
  }
};

/**
 * Stagger container with slower animation
 */
export const staggerChildrenSlow: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2
    }
  }
};

/**
 * Hover animation - scale up slightly
 * Use: whileHover="hover"
 */
export const hoverScale: Variants = {
  hover: {
    scale: 1.02,
    transition: { duration: 0.2 }
  }
};

/**
 * Hover animation - lift with shadow
 * Use: whileHover="hover"
 */
export const hoverLift: Variants = {
  hover: {
    y: -4,
    transition: { duration: 0.2 }
  }
};

/**
 * Tap animation - scale down slightly
 * Use: whileTap="tap"
 */
export const tapScale: Variants = {
  tap: {
    scale: 0.98,
    transition: { duration: 0.1 }
  }
};

/**
 * Rotate animation (for loading spinners)
 * Use: variants={rotate} animate="animate"
 */
export const rotate: Variants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: "linear"
    }
  }
};

/**
 * Pulse animation (for attention)
 * Use: variants={pulse} animate="animate"
 */
export const pulse: Variants = {
  animate: {
    scale: [1, 1.05, 1],
    opacity: [1, 0.8, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut"
    }
  }
};

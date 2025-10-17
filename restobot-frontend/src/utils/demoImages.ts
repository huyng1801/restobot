// Demo constants for menu items with images
export const DEMO_MENU_IMAGES = {
  placeholder: '/api/placeholder/200/200',
  
  // Some example URLs for testing
  examples: [
    'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=200&h=200&fit=crop'
  ]
};

// Helper function to get a random demo image
export const getRandomDemoImage = () => {
  const examples = DEMO_MENU_IMAGES.examples;
  return examples[Math.floor(Math.random() * examples.length)];
};
const fs = require('fs');
const path = require('path');

function copyRecursiveSync(src, dest) {
  const exists = fs.existsSync(src);
  const stats = exists && fs.statSync(src);
  const isDirectory = exists && stats.isDirectory();
  
  if (isDirectory) {
    if (!fs.existsSync(dest)) {
      fs.mkdirSync(dest, { recursive: true });
    }
    fs.readdirSync(src).forEach(childItemName => {
      copyRecursiveSync(
        path.join(src, childItemName),
        path.join(dest, childItemName)
      );
    });
  } else {
    fs.copyFileSync(src, dest);
  }
}

try {
  const frontendDir = path.join(__dirname, '..', 'frontend');
  const publicDir = path.join(__dirname, '..', 'public');
  
  // Remove public directory if it exists
  if (fs.existsSync(publicDir)) {
    fs.rmSync(publicDir, { recursive: true, force: true });
  }
  
  // Copy all files from frontend to public
  copyRecursiveSync(frontendDir, publicDir);
  
  console.log('✅ Frontend files copied to public/ directory');
} catch (error) {
  console.error('❌ Error copying frontend files:', error);
  process.exit(1);
}

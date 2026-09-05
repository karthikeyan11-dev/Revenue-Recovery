import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const projectRoot = path.resolve(__dirname, '../..');
const frontendDir = path.resolve(__dirname, '..');
const backendDir = path.resolve(projectRoot, 'backend');
const openapiJsonPath = path.resolve(frontendDir, 'openapi.json');
const outputDir = path.resolve(frontendDir, 'src/api/generated');

async function generateSdk() {
  console.log('🚀 Starting OpenAPI TypeScript SDK generation...');

  // Step 1: Export OpenAPI JSON from FastAPI Backend
  let openapiFound = false;

  // Try python export script first (offline capable)
  const pythonBin = fs.existsSync(path.resolve(backendDir, 'venv/bin/python'))
    ? path.resolve(backendDir, 'venv/bin/python')
    : 'python3';

  try {
    console.log('📦 Exporting OpenAPI schema from FastAPI backend app...');
    execSync(`${pythonBin} scripts/export_openapi.py "${openapiJsonPath}"`, {
      cwd: backendDir,
      stdio: 'inherit',
    });
    openapiFound = true;
  } catch (err) {
    console.warn('⚠️ Could not run Python export script, trying HTTP fetch from http://localhost:8000/openapi.json...');
    try {
      const res = await fetch('http://localhost:8000/openapi.json');
      if (res.ok) {
        const data = await res.json();
        fs.writeFileSync(openapiJsonPath, JSON.stringify(data, null, 2), 'utf-8');
        openapiFound = true;
      }
    } catch {
      // Ignored
    }
  }

  if (!openapiFound || !fs.existsSync(openapiJsonPath)) {
    throw new Error('❌ Failed to retrieve openapi.json from backend application.');
  }

  // Step 2: Generate TypeScript Client SDK
  console.log(`⚙️ Generating TypeScript SDK into ${outputDir}...`);

  // Ensure output directory exists
  if (fs.existsSync(outputDir)) {
    fs.rmSync(outputDir, { recursive: true, force: true });
  }

  execSync(`npx openapi-typescript-codegen --input "${openapiJsonPath}" --output "${outputDir}" --client fetch --useUnionTypes`, {
    cwd: frontendDir,
    stdio: 'inherit',
  });

  // Clean up temporary schema file
  if (fs.existsSync(openapiJsonPath)) {
    fs.unlinkSync(openapiJsonPath);
  }

  console.log('✅ OpenAPI TypeScript SDK generated successfully!');
}

generateSdk().catch((err) => {
  console.error(err);
  process.exit(1);
});

/**
 * Utility to parse local project folders directly in the browser via
 * webkitdirectory (Folder Picker dialog) or Drag-and-Drop DataTransfer.
 * Filters out node_modules, .git, build artifacts, and binaries,
 * extracting manifest files and source code into a unified repo manifest.
 */

const IGNORE_DIRS = new Set([
  'node_modules',
  '.git',
  '.svn',
  '.hg',
  '__pycache__',
  '.pytest_cache',
  'dist',
  'build',
  'out',
  '.next',
  '.nuxt',
  '.venv',
  'venv',
  'env',
  '.idea',
  '.vscode',
  'coverage',
  '.turbo',
  '.cache',
  'fixie',
  'bin',
  'obj',
  'target',
  '.gradle',
]);

const IGNORE_EXTENSIONS = new Set([
  'exe', 'bin', 'dll', 'so', 'dylib', 'o', 'a',
  'png', 'jpg', 'jpeg', 'gif', 'ico', 'svg', 'webp',
  'zip', 'tar', 'gz', '7z', 'rar',
  'pdf', 'woff', 'woff2', 'ttf', 'eot',
  'mp4', 'mp3', 'wav', 'mov', 'avi',
  'lock', 'pyc', 'class', 'jar',
]);

const MANIFEST_PATTERNS = new Set([
  'package.json',
  'tsconfig.json',
  'cmakelists.txt',
  'requirements.txt',
  'pyproject.toml',
  'cargo.toml',
  'pom.xml',
  'build.gradle',
  'dockerfile',
  'makefile',
  'gemfile',
  'go.mod',
]);

const MAX_SOURCE_FILES = 50;
const MAX_FILE_SIZE = 80 * 1024; // 80 KB

/**
 * Filter and convert a list of File objects with webkitRelativePath into a repoManifest.
 */
export async function parseFilesToManifest(files) {
  const fileArray = Array.from(files || []);
  if (fileArray.length === 0) {
    throw new Error('No files found in selected folder.');
  }

  // Derive repo name from the top-level directory of webkitRelativePath
  let rootName = 'Uploaded-Project';
  if (fileArray[0].webkitRelativePath) {
    const firstPart = fileArray[0].webkitRelativePath.split('/')[0];
    if (firstPart) rootName = firstPart;
  } else if (fileArray[0].name) {
    rootName = fileArray[0].name.replace(/\.[^/.]+$/, '') || 'Uploaded-Project';
  }

  // Filter out noise
  const validFiles = fileArray.filter((file) => {
    const relPath = (file.webkitRelativePath || file.name).replace(/\\/g, '/');
    const parts = relPath.split('/');

    // Check directory components
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i].toLowerCase();
      if (IGNORE_DIRS.has(part) || (part.startsWith('.') && part !== '.')) {
        return false;
      }
    }

    const fileName = parts[parts.length - 1];
    const ext = fileName.includes('.')
      ? fileName.split('.').pop().toLowerCase()
      : '';
    if (IGNORE_EXTENSIONS.has(ext)) return false;

    return true;
  });

  if (validFiles.length === 0) {
    throw new Error(
      'Folder contains only ignored files (node_modules, .git, or binary assets).'
    );
  }

  // Sort manifests first, then shallow paths
  validFiles.sort((a, b) => {
    const nameA = a.name.toLowerCase();
    const nameB = b.name.toLowerCase();
    const isManA = MANIFEST_PATTERNS.has(nameA);
    const isManB = MANIFEST_PATTERNS.has(nameB);
    if (isManA && !isManB) return -1;
    if (!isManA && isManB) return 1;
    return (a.webkitRelativePath || a.name).length - (b.webkitRelativePath || b.name).length;
  });

  const fileTree = [];
  const manifestFiles = {};
  const sourceFiles = {};

  let textReadCount = 0;

  for (const file of validFiles) {
    const fullRelPath = (file.webkitRelativePath || file.name).replace(/\\/g, '/');
    const parts = fullRelPath.split('/');
    // Strip root folder name if present
    const relPath = parts.length > 1 ? parts.slice(1).join('/') : fullRelPath;
    const fileName = file.name;
    const ext = fileName.includes('.')
      ? fileName.split('.').pop().toLowerCase()
      : '';
    const isManifest = MANIFEST_PATTERNS.has(fileName.toLowerCase());

    fileTree.push({
      path: relPath,
      name: fileName,
      extension: ext,
      size: file.size,
      is_manifest: isManifest,
    });

    if (file.size <= MAX_FILE_SIZE && textReadCount < MAX_SOURCE_FILES) {
      try {
        const text = await file.text();
        if (isManifest) {
          manifestFiles[relPath] = text;
        } else {
          sourceFiles[relPath] = text;
        }
        textReadCount++;
      } catch (err) {
        console.warn(`Could not read text from ${relPath}:`, err);
      }
    }
  }

  return {
    repo_name: rootName,
    repo_path: rootName,
    total_files: fileTree.length,
    file_tree: fileTree,
    manifest_files: manifestFiles,
    source_files: sourceFiles,
  };
}

/**
 * Traverse HTML5 DataTransfer items to extract all files recursively from dropped folders.
 */
export async function getFilesFromDataTransfer(dataTransfer) {
  const files = [];
  const items = dataTransfer.items;
  if (!items) return files;

  async function traverseEntry(entry, path = '') {
    if (entry.isFile) {
      const file = await new Promise((resolve, reject) => {
        entry.file(resolve, reject);
      });
      // Attach webkitRelativePath for consistent downstream processing
      Object.defineProperty(file, 'webkitRelativePath', {
        value: path ? `${path}/${file.name}` : file.name,
        writable: false,
      });
      files.push(file);
    } else if (entry.isDirectory) {
      const dirName = entry.name;
      if (IGNORE_DIRS.has(dirName.toLowerCase()) || dirName.startsWith('.')) {
        return; // Ignore unwanted folder
      }

      const dirReader = entry.createReader();
      const entries = await new Promise((resolve) => {
        const result = [];
        function readBatch() {
          dirReader.readEntries((batch) => {
            if (batch.length === 0) {
              resolve(result);
            } else {
              result.push(...batch);
              readBatch();
            }
          });
        }
        readBatch();
      });

      for (const child of entries) {
        await traverseEntry(child, path ? `${path}/${dirName}` : dirName);
      }
    }
  }

  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (item.webkitGetAsEntry) {
      const entry = item.webkitGetAsEntry();
      if (entry) {
        await traverseEntry(entry);
      }
    } else if (item.kind === 'file') {
      const file = item.getAsFile();
      if (file) files.push(file);
    }
  }

  return files;
}

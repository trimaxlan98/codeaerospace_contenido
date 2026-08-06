import { useState, useRef, useEffect } from 'react';
import { 
  Folder, 
  FolderPlus, 
  File, 
  FileText, 
  Image as ImageIcon, 
  FileSpreadsheet, 
  ChevronDown, 
  ChevronRight, 
  ChevronLeft, 
  Bell, 
  Upload, 
  Search, 
  Sparkles, 
  Plus, 
  X, 
  MoreVertical, 
  Trash2, 
  Clock, 
  Star, 
  Users, 
  HardDrive, 
  Check, 
  AlertCircle,
  Menu,
  Grid,
  Filter,
  ArrowUpRight
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { GlowCard } from './components/GlowCard.jsx';

// Initial Mock Folders
const INITIAL_FOLDERS = [
  {
    id: 'folder-1',
    name: 'Marketing Collateral',
    color: '#D97706', // Cream/Amber
    bgColor: 'rgba(217, 119, 6, 0.1)',
    borderColor: 'rgba(217, 119, 6, 0.25)',
    fileCount: 35,
    size: '201 MB',
    files: [
      { id: 'f1-1', name: 'q3-campaign-brief.pdf', type: 'PDF', size: '2.4 MB', date: '2 days ago', favorite: true, sizeBytes: 2400000 },
      { id: 'f1-2', name: 'social-media-assets.zip', type: 'ZIP', size: '185 MB', date: '1 week ago', favorite: false, sizeBytes: 185000000 },
      { id: 'f1-3', name: 'ad-copy-final.txt', type: 'TXT', size: '14 KB', date: 'Yesterday', favorite: true, sizeBytes: 14000 }
    ]
  },
  {
    id: 'folder-2',
    name: 'Design Resources',
    color: '#A855F7', // Purple
    bgColor: 'rgba(168, 85, 247, 0.1)',
    borderColor: 'rgba(168, 85, 247, 0.25)',
    fileCount: 18,
    size: '1.2 GB',
    files: [
      { id: 'f2-1', name: 'app-wireframes.pdf', type: 'PDF', size: '15.8 MB', date: '4 days ago', favorite: true, sizeBytes: 15800000 },
      { id: 'f2-2', name: 'ui-kit-v2.fig', type: 'FIG', size: '42 MB', date: '3 hours ago', favorite: true, sizeBytes: 42000000 },
      { id: 'f2-3', name: 'brand-guidelines.pdf', type: 'PDF', size: '12.4 MB', date: '2 weeks ago', favorite: false, sizeBytes: 12400000 }
    ]
  },
  {
    id: 'folder-3',
    name: 'Product Roadmaps',
    color: '#10B981', // Green
    bgColor: 'rgba(16, 185, 129, 0.1)',
    borderColor: 'rgba(16, 185, 129, 0.25)',
    fileCount: 12,
    size: '45 MB',
    files: [
      { id: 'f3-1', name: 'product-spec-v3.txt', type: 'TXT', size: '28 KB', date: '2 hours ago', favorite: false, sizeBytes: 28000 },
      { id: 'f3-2', name: 'launch-plan.xls', type: 'XLS', size: '1.2 MB', date: 'Yesterday', favorite: true, sizeBytes: 1200000 },
      { id: 'f3-3', name: 'milestones-gantt.pdf', type: 'PDF', size: '3.1 MB', date: '5 days ago', favorite: false, sizeBytes: 3100000 }
    ]
  },
  {
    id: 'folder-4',
    name: 'Finance Reports',
    color: '#EF4444', // Red
    bgColor: 'rgba(239, 68, 68, 0.1)',
    borderColor: 'rgba(239, 68, 68, 0.25)',
    fileCount: 8,
    size: '12 MB',
    files: [
      { id: 'f4-1', name: 'q2-balance-sheet.xls', type: 'XLS', size: '4.8 MB', date: 'Yesterday', favorite: true, sizeBytes: 4800000 },
      { id: 'f4-2', name: 'forecast-2026.xls', type: 'XLS', size: '5.2 MB', date: '3 days ago', favorite: false, sizeBytes: 5200000 },
      { id: 'f4-3', name: 'audited-statements-25.pdf', type: 'PDF', size: '2.0 MB', date: '1 month ago', favorite: false, sizeBytes: 2000000 }
    ]
  }
];

// Initial Recent files (at Root)
const INITIAL_RECENT_FILES = [
  { id: 'rf-1', name: 'hero-illustration.jpg', type: 'JPG', size: '404 KB', date: '2 hours ago', sizeBytes: 413696, favorite: true },
  { id: 'rf-2', name: 'revenue-2026.xls', type: 'XLS', size: '1.2 MB', date: '2 hours ago', sizeBytes: 1258291, favorite: false },
  { id: 'rf-3', name: 'dashboard-spec.txt', type: 'TXT', size: '45 KB', date: '1 hour ago', sizeBytes: 46080, favorite: true },
  { id: 'rf-4', name: 'presentation-draft.pdf', type: 'PDF', size: '4.2 MB', date: '20 mins ago', sizeBytes: 4404019, favorite: false }
];

export default function FileManager() {
  const [folders, setFolders] = useState(INITIAL_FOLDERS);
  const [recentFiles, setRecentFiles] = useState(INITIAL_RECENT_FILES);
  const [trashItems, setTrashItems] = useState([]); // Storage for items in trash
  
  // Navigation states
  const [activeNav, setActiveNav] = useState('overview'); // overview, files, shared, favorite, recent, trash
  const [currentFolder, setCurrentFolder] = useState(null); // null means root/overview
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Modals / Dropdowns / Dialogs
  const [isUpgradeOpen, setIsUpgradeOpen] = useState(false);
  const [uploadToast, setUploadToast] = useState(null);

  const fileInputRef = useRef(null);

  // Keyboard shortcut for Search (CMD+K / CTRL+K)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('dashboard-search');
        if (searchInput) searchInput.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Sync Pointer movement at Root Dashboard as well
  useEffect(() => {
    const syncPointer = (e) => {
      const { clientX: x, clientY: y } = e;
      document.documentElement.style.setProperty('--x', x.toFixed(2));
      document.documentElement.style.setProperty('--y', y.toFixed(2));
    };
    document.addEventListener('pointermove', syncPointer);
    return () => document.removeEventListener('pointermove', syncPointer);
  }, []);

  // Progress Bar configuration
  const TOTAL_STORAGE = 100; // GB
  const CATEGORIES = [
    { name: 'Documents', size: 25.4, color: '#6366F1' }, // Indigo
    { name: 'Images', size: 30.2, color: '#EC4899' },    // Pink
    { name: 'Media', size: 15.5, color: '#A855F7' },     // Purple
    { name: 'Others', size: 9.01, color: '#F59E0B' },    // Orange/Cream
  ];
  const usedStorage = CATEGORIES.reduce((acc, cat) => acc + cat.size, 0); // 80.11
  const freeStorage = TOTAL_STORAGE - usedStorage; // 19.89

  // Filter logic based on search query and current navigation tab
  const getFilteredFolders = () => {
    let list = folders;
    if (activeNav === 'trash') return [];
    
    // If we're deep inside a folder, we don't display folder cards inside it
    if (currentFolder) return [];

    if (searchQuery) {
      list = list.filter(f => f.name.toLowerCase().includes(searchQuery.toLowerCase()));
    }

    if (activeNav === 'favorite') {
      // Show folders that have starred files, or just show directories
      return list.filter(f => f.files.some(sf => sf.favorite));
    }

    return list;
  };

  const getFilteredFiles = () => {
    if (activeNav === 'trash') {
      return trashItems.filter(item => 
        searchQuery ? item.name.toLowerCase().includes(searchQuery.toLowerCase()) : true
      );
    }

    let allFiles = [];
    if (currentFolder) {
      // Show files inside the current folder
      const folder = folders.find(f => f.id === currentFolder.id);
      allFiles = folder ? folder.files : [];
    } else {
      // At root level
      if (activeNav === 'recent' || activeNav === 'overview') {
        allFiles = recentFiles;
      } else if (activeNav === 'favorite') {
        // Starred files from everywhere
        const starredRecent = recentFiles.filter(f => f.favorite);
        const starredInFolders = folders.flatMap(f => f.files.filter(sf => sf.favorite).map(sf => ({ ...sf, folderId: f.id })));
        allFiles = [...starredRecent, ...starredInFolders];
      } else {
        // 'My Files' tab - show all root files + files inside folders with folder tags
        const root = recentFiles;
        const inFolders = folders.flatMap(f => f.files.map(sf => ({ ...sf, folderName: f.name, folderId: f.id })));
        allFiles = [...root, ...inFolders];
      }
    }

    if (searchQuery) {
      allFiles = allFiles.filter(f => f.name.toLowerCase().includes(searchQuery.toLowerCase()));
    }

    return allFiles;
  };

  // Star Toggle
  const toggleFavorite = (fileId, e) => {
    e.stopPropagation();
    // Toggle in root files
    setRecentFiles(prev => prev.map(f => f.id === fileId ? { ...f, favorite: !f.favorite } : f));
    // Toggle in folders
    setFolders(prev => prev.map(folder => ({
      ...folder,
      files: folder.files.map(f => f.id === fileId ? { ...f, favorite: !f.favorite } : f)
    })));
  };

  // Move Item to Trash
  const moveToTrash = (file, e) => {
    if (e) e.stopPropagation();
    
    // Add to trash list
    setTrashItems(prev => [...prev, { ...file, deletedAt: new Date().toLocaleTimeString() }]);

    // Remove from root files
    setRecentFiles(prev => prev.filter(f => f.id !== file.id));

    // Remove from folders
    setFolders(prev => prev.map(folder => ({
      ...folder,
      files: folder.files.filter(f => f.id !== file.id)
    })));

    showToast(`"${file.name}" movido a la Papelera.`);
  };

  // Restore from Trash
  const restoreFromTrash = (file, e) => {
    e.stopPropagation();
    setTrashItems(prev => prev.filter(f => f.id !== file.id));
    
    // If it was a folder file, we restore to folder, otherwise root
    if (file.folderId) {
      setFolders(prev => prev.map(f => f.id === file.folderId ? { ...f, files: [...f.files, file] } : f));
    } else {
      setRecentFiles(prev => [file, ...prev]);
    }
    showToast(`"${file.name}" restaurado.`);
  };

  // Permanent Delete
  const deletePermanently = (fileId, e) => {
    e.stopPropagation();
    setTrashItems(prev => prev.filter(f => f.id !== fileId));
    showToast(`Elemento eliminado permanentemente.`);
  };

  // Handle Trigger Upload File
  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    if (!uploadedFile) return;

    // Determine type and size formatting
    const name = uploadedFile.name;
    const extension = name.split('.').pop().toUpperCase();
    const sizeMB = (uploadedFile.size / (1024 * 1024)).toFixed(2);
    const sizeStr = sizeMB > 1 ? `${sizeMB} MB` : `${(uploadedFile.size / 1024).toFixed(0)} KB`;

    const newFileObj = {
      id: `uploaded-${Date.now()}`,
      name: name,
      type: extension,
      size: sizeStr,
      date: 'Just now',
      sizeBytes: uploadedFile.size,
      favorite: false
    };

    if (currentFolder) {
      // Add inside the current open folder
      setFolders(prev => prev.map(folder => {
        if (folder.id === currentFolder.id) {
          return {
            ...folder,
            fileCount: folder.fileCount + 1,
            files: [newFileObj, ...folder.files]
          };
        }
        return folder;
      }));
    } else {
      // Add to root files list
      setRecentFiles(prev => [newFileObj, ...prev]);
    }

    showToast(`Archivo "${name}" subido con éxito.`);
    // Reset file input
    e.target.value = '';
  };

  const showToast = (message) => {
    setUploadToast(message);
    setTimeout(() => {
      setUploadToast(null);
    }, 4000);
  };

  // Icon Mappers
  const getFileIcon = (type) => {
    const t = type?.toUpperCase();
    if (t === 'PDF') return { icon: <FileText className="text-purple-400" />, bg: 'bg-purple-500/10 border-purple-500/20' };
    if (t === 'XLS' || t === 'CSV') return { icon: <FileSpreadsheet className="text-emerald-400" />, bg: 'bg-emerald-500/10 border-emerald-500/20' };
    if (['JPG', 'PNG', 'WEBP', 'FIG', 'SVG'].includes(t)) return { icon: <ImageIcon className="text-indigo-400" />, bg: 'bg-indigo-500/10 border-indigo-500/20' };
    return { icon: <File className="text-slate-400" />, bg: 'bg-slate-500/10 border-slate-500/20' };
  };

  const getFolderColor = (folderName) => {
    if (folderName.includes('Marketing')) return { color: '#F59E0B', text: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' };
    if (folderName.includes('Design')) return { color: '#A855F7', text: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' };
    if (folderName.includes('Product')) return { color: '#10B981', text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' };
    return { color: '#EF4444', text: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20' };
  };

  return (
    <div className="flex h-full w-full select-none bg-[#0B0F19] text-[#FFFFFF] font-sans antialiased overflow-hidden">
      
      {/* Hidden File Input */}
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        className="hidden" 
      />

      {/* SUCCESS TOAST NOTIFICATION */}
      {uploadToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-xl border border-emerald-500/20 bg-[#151A23]/90 px-4 py-3 shadow-[0_10px_40px_rgba(16,185,129,0.15)] backdrop-blur-md animate-in fade-in slide-in-from-bottom-5 duration-300">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-emerald-500/10 text-emerald-400">
            <Check className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-white">Transacción Completa</h4>
            <p className="text-xs text-slate-400">{uploadToast}</p>
          </div>
        </div>
      )}

      {/* SIDEBAR (IZQUIERDA) */}
      <aside 
        className={cn(
          "relative z-20 flex h-full flex-col border-r border-white/[0.06] bg-[#0F131E] transition-all duration-300 shrink-0",
          isCollapsed ? "w-[78px]" : "w-[260px]"
        )}
      >
        
        {/* COLLAPSIBLE SIDEBAR BUTTON */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="absolute -right-3 top-1/2 z-30 hidden h-6 w-6 -translate-y-1/2 place-items-center rounded-full border border-white/[0.08] bg-[#0B0F19] text-slate-400 shadow-md transition-all hover:text-white lg:grid"
        >
          <ChevronLeft className={cn("h-4 w-4 transition-transform duration-300", isCollapsed && "rotate-180")} />
        </button>

        {/* SIDEBAR HEADER */}
        <div className="flex h-16 items-center justify-between px-5 border-b border-white/[0.04]">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#6366F1] shadow-[0_0_12px_rgba(99,102,241,0.4)]">
              <span className="text-lg font-bold text-white">☺</span>
            </div>
            {!isCollapsed && (
              <span className="font-display text-[15px] font-semibold tracking-tight text-white whitespace-nowrap">
                File Manager
              </span>
            )}
          </div>
          {!isCollapsed && (
            <button className="rounded p-1 text-slate-500 hover:bg-white/5 hover:text-slate-300 md:block hidden">
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* USER PROFILE CARD WITH BENTO STYLE */}
        <div className="p-4">
          <div className={cn(
            "group relative flex items-center gap-3 rounded-xl bg-[#151A23]/60 p-3 border border-white/[0.06] overflow-hidden transition-all duration-300",
            "hover:shadow-[0_2px_12px_rgba(255,255,255,0.02)] hover:-translate-y-0.5 will-change-transform cursor-pointer",
            isCollapsed && "justify-center p-2"
          )}>
            {/* Bento Absolute Background dots */}
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[length:4px_4px]" />
            </div>

            <div className="h-9 w-9 shrink-0 overflow-hidden rounded-full bg-slate-700 border border-white/10 flex items-center justify-center font-bold text-slate-300 text-xs">
              AB
            </div>
            {!isCollapsed && (
              <div className="min-w-0 flex-1 leading-normal text-left z-10">
                <h4 className="truncate text-xs font-semibold text-white">Alexander Bell</h4>
                <p className="truncate text-[10px] text-slate-400">Manager</p>
              </div>
            )}
            {!isCollapsed && <ChevronDown className="h-3 w-3 text-slate-400 z-10" />}

            {/* Bento Absolute Highlight Border gradient */}
            <div className="absolute inset-0 -z-10 rounded-xl p-px bg-gradient-to-br from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
          </div>
        </div>

        {/* MENU NAVIGATION */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-6">
          <div className="space-y-1">
            {!isCollapsed && (
              <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                Menu
              </p>
            )}
            
            {/* Nav Items */}
            {[
              { id: 'overview', label: 'Overview', icon: <HardDrive className="h-4 w-4" /> },
              { id: 'files', label: 'My Files', icon: <Folder className="h-4 w-4" /> },
              { id: 'shared', label: 'Shared Files', icon: <Users className="h-4 w-4" /> },
              { id: 'favorite', label: 'Favorite', icon: <Star className="h-4 w-4" /> },
              { id: 'recent', label: 'Recent', icon: <Clock className="h-4 w-4" /> },
              { id: 'trash', label: 'Trash', icon: <Trash2 className="h-4 w-4" /> },
            ].map(item => {
              const active = activeNav === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveNav(item.id);
                    setCurrentFolder(null); // Reset folder path on tab click
                  }}
                  className={cn(
                    "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium transition-all duration-150 text-left",
                    active 
                      ? "bg-[#151A23] text-white border border-white/[0.05] shadow-sm font-semibold" 
                      : "text-slate-400 hover:bg-[#151A23]/30 hover:text-white"
                  )}
                >
                  <span className={cn(active ? "text-[#6366F1]" : "text-slate-400")}>
                    {item.icon}
                  </span>
                  {!isCollapsed && <span className="truncate">{item.label}</span>}
                </button>
              );
            })}
          </div>
        </div>

        {/* UPGRADE STORAGE WIDGET WITH BENTO STYLE */}
        {!isCollapsed && (
          <div className="p-4 mt-auto">
            <div className="group relative rounded-2xl border border-white/[0.06] bg-[#121620] p-4 text-left shadow-lg overflow-hidden transition-all duration-300 hover:shadow-[0_2px_12px_rgba(255,255,255,0.02)] hover:-translate-y-0.5 will-change-transform">
              
              {/* Bento Absolute Background dots */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[length:4px_4px]" />
              </div>

              <div className="flex items-center justify-between mb-2 z-10 relative">
                <span className="text-xs font-semibold text-white">Upgrade Storage</span>
                <Sparkles className="h-3.5 w-3.5 text-indigo-400 animate-pulse" />
              </div>
              
              {/* Segmented Progress Bar */}
              <div className="flex gap-0.5 h-1.5 mb-2.5 z-10 relative">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(seg => (
                  <div 
                    key={seg} 
                    className={cn(
                      "flex-1 h-full rounded-sm transition-all duration-300",
                      seg <= 8 
                        ? "bg-[#6366F1] shadow-[0_0_8px_rgba(99,102,241,0.6)]" 
                        : "bg-white/[0.08]"
                    )}
                  />
                ))}
              </div>

              <div className="flex justify-between text-[10px] text-slate-400 mb-4 z-10 relative">
                <span>{usedStorage.toFixed(2)} GB of {TOTAL_STORAGE} GB Used</span>
                <span className="font-semibold text-indigo-400">80%</span>
              </div>

              <button 
                onClick={() => setIsUpgradeOpen(true)}
                className="w-full relative z-10 rounded-xl bg-indigo-600 px-3 py-2 text-xs font-semibold text-white hover:bg-indigo-500 active:bg-indigo-700 transition-all duration-150 shadow-[0_4px_12px_rgba(99,102,241,0.2)]"
              >
                Upgrade Plan
              </button>

              {/* Bento Absolute Highlight Border gradient */}
              <div className="absolute inset-0 -z-10 rounded-2xl p-px bg-gradient-to-br from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
            </div>
          </div>
        )}

      </aside>

      {/* CONTENIDO PRINCIPAL (DERECHA) */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-[#0B0F19]">
        
        {/* HEADER SUPERIOR */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-white/[0.04] bg-[#0F131E]/30 px-6 backdrop-blur-md">
          
          {/* Barra de Búsqueda */}
          <div className="relative w-[min(320px,100%)]">
            <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <input
              id="dashboard-search"
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-xl border border-white/[0.06] bg-[#0F131E] py-1.5 pl-9 pr-12 text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#6366F1] focus:border-transparent transition-all"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 rounded bg-white/5 border border-white/[0.08] px-1 py-0.5 text-[9px] font-mono text-slate-400 select-none">
              ⌘ K
            </span>
          </div>

          {/* Acciones a la Derecha */}
          <div className="flex items-center gap-4">
            
            {/* Campana de Notificación */}
            <button className="relative rounded-xl border border-white/[0.06] bg-[#0F131E] p-2 text-slate-400 hover:text-white hover:bg-[#151A23] transition-all">
              <Bell className="h-4 w-4" />
              <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-rose-500 shadow-[0_0_6px_#EF4444]" />
            </button>

            {/* Upload Button */}
            <button 
              onClick={handleUploadClick}
              className="flex items-center gap-2 rounded-xl bg-[#6366F1] px-4 py-2 text-xs font-semibold text-white shadow-[0_4px_16px_rgba(99,102,241,0.25)] hover:bg-[#5558E6] active:bg-[#4346D0] transition-all"
            >
              <Upload className="h-3.5 w-3.5" />
              <span>Upload File</span>
            </button>
          </div>

        </header>

        {/* CUERPO DEL FILES MANAGER (CON SCROLL) */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          
          {/* SECCIÓN 1: ALMACENAMIENTO CON BENTO STYLE (OVERVIEW) */}
          {activeNav === 'overview' && !currentFolder && (
            <div className="group relative rounded-2xl border border-white/[0.05] bg-[#151A23]/45 p-5 shadow-[0_12px_40px_rgba(0,0,0,0.15)] text-left overflow-hidden transition-all duration-300 hover:shadow-[0_2px_12px_rgba(255,255,255,0.02)] hover:-translate-y-0.5 will-change-transform">
              
              {/* Bento Absolute Background dots */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[length:4px_4px]" />
              </div>

              <div className="flex items-center justify-between mb-3 relative z-10">
                <div className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4 text-slate-400" />
                  <span className="text-xs font-semibold text-slate-300">Resumen de Almacenamiento</span>
                </div>
                <p className="text-xs text-slate-400">
                  <span className="text-white font-bold">{usedStorage.toFixed(1)} GB</span> de {TOTAL_STORAGE} GB
                </p>
              </div>

              {/* Barra de progreso segmentada de almacenamiento horizontal */}
              <div className="flex gap-1 h-3.5 rounded-full overflow-hidden mb-4 bg-white/[0.04] p-0.5 border border-white/[0.04] relative z-10">
                {CATEGORIES.map((cat, idx) => {
                  const percent = (cat.size / TOTAL_STORAGE) * 100;
                  return (
                    <div 
                      key={idx}
                      title={`${cat.name}: ${cat.size} GB`}
                      className="h-full rounded-sm transition-all duration-500 first:rounded-l-full"
                      style={{ 
                        width: `${percent}%`, 
                        backgroundColor: cat.color,
                        boxShadow: `0 0 10px ${cat.color}35`
                      }}
                    />
                  );
                })}
                {/* Espacio Libre */}
                <div 
                  title={`Free Space: ${freeStorage.toFixed(2)} GB`}
                  className="h-full bg-white/[0.06] rounded-r-full transition-all duration-500"
                  style={{ width: `${(freeStorage / TOTAL_STORAGE) * 100}%` }}
                />
              </div>

              {/* Leyenda con puntos de color */}
              <div className="flex flex-wrap gap-x-5 gap-y-2 relative z-10">
                {CATEGORIES.map((cat, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: cat.color }} />
                    <span className="text-[11px] text-slate-400">{cat.name}</span>
                    <span className="text-[11px] font-mono text-slate-300">({cat.size} GB)</span>
                  </div>
                ))}
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-white/20" />
                  <span className="text-[11px] text-slate-400">Free Space</span>
                  <span className="text-[11px] font-mono text-slate-300">({freeStorage.toFixed(1)} GB)</span>
                </div>
              </div>

              {/* Bento Absolute Highlight Border gradient */}
              <div className="absolute inset-0 -z-10 rounded-2xl p-px bg-gradient-to-br from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
            </div>
          )}

          {/* SECCIÓN 2: RUTA DE CARPETA (BREADCRUMBS) */}
          {currentFolder && (
            <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
              <button 
                onClick={() => setCurrentFolder(null)}
                className="hover:text-white transition-colors"
              >
                Root
              </button>
              <ChevronRight className="h-3 w-3" />
              <span className="text-white font-semibold">{currentFolder.name}</span>
            </div>
          )}

          {/* SECCIÓN 3: VISTA DE CARPETAS CON BENTO STYLE */}
          {getFilteredFolders().length > 0 && (
            <div className="space-y-4 text-left">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white tracking-wide">Carpetas</h3>
                <span className="text-[10px] text-slate-500 font-mono uppercase">
                  {getFilteredFolders().length} Folders
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5">
                {getFilteredFolders().map((folder) => {
                  const styleMeta = getFolderColor(folder.name);
                  return (
                    <div 
                      key={folder.id}
                      onClick={() => setCurrentFolder(folder)}
                      className="group relative cursor-pointer rounded-xl border border-white/[0.08] bg-[#151A23] p-4 overflow-hidden transition-all duration-300 hover:shadow-[0_2px_12px_rgba(255,255,255,0.03)] hover:-translate-y-0.5 will-change-transform"
                    >
                      {/* Bento Absolute Background dots */}
                      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[length:4px_4px]" />
                      </div>

                      <div className="flex items-start justify-between relative z-10">
                        {/* Folder icon customizable */}
                        <div className={cn("rounded-xl p-2.5 transition-colors duration-200", styleMeta.bg, styleMeta.border)}>
                          <Folder className={cn("h-5 w-5", styleMeta.text)} />
                        </div>
                        
                        <button 
                          onClick={(e) => e.stopPropagation()}
                          className="rounded-lg p-1 text-slate-500 hover:bg-white/5 hover:text-slate-300"
                        >
                          <MoreVertical className="h-4 w-4" />
                        </button>
                      </div>

                      <div className="mt-4 relative z-10">
                        <h4 className="text-xs font-semibold text-white group-hover:text-indigo-400 transition-colors">
                          {folder.name}
                        </h4>
                        <div className="mt-1 flex items-center gap-1.5 text-[10px] text-slate-400">
                          <span>{folder.fileCount} archivos</span>
                          <span className="text-slate-600">•</span>
                          <span>{folder.size}</span>
                        </div>
                      </div>

                      {/* Bento Absolute Highlight Border gradient */}
                      <div className="absolute inset-0 -z-10 rounded-xl p-px bg-gradient-to-br from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* SECCIÓN 4: RECENT FILES / FILE LIST WITH BENTO STYLE */}
          <div className="space-y-4 text-left">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white tracking-wide">
                {activeNav === 'trash' ? 'Papelera de Reciclaje' : currentFolder ? 'Archivos de la Carpeta' : 'Archivos Recientes'}
              </h3>
              <span className="text-[10px] text-slate-500 font-mono uppercase">
                {getFilteredFiles().length} Files
              </span>
            </div>

            {getFilteredFiles().length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 rounded-2xl border border-dashed border-white/5 bg-[#151A23]/10">
                <AlertCircle className="h-8 w-8 text-slate-600 mb-2.5" />
                <p className="text-xs text-slate-400">No se encontraron archivos en este directorio.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {getFilteredFiles().map((file) => {
                  const iconMeta = getFileIcon(file.type);
                  return (
                    <div 
                      key={file.id}
                      className="group relative flex flex-col justify-between rounded-xl border border-white/[0.08] bg-[#151A23]/80 p-3.5 overflow-hidden transition-all duration-300 hover:shadow-[0_2px_12px_rgba(255,255,255,0.03)] hover:-translate-y-0.5 will-change-transform"
                    >
                      {/* Bento Absolute Background dots */}
                      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[length:4px_4px]" />
                      </div>

                      {/* Top elements */}
                      <div className="flex items-start justify-between relative z-10">
                        <div className={cn("rounded-lg border p-2", iconMeta.bg)}>
                          {iconMeta.icon}
                        </div>
                        
                        <div className="flex items-center gap-1">
                          {/* Star/Fav button */}
                          {activeNav !== 'trash' && (
                            <button 
                              onClick={(e) => toggleFavorite(file.id, e)}
                              className="rounded-lg p-1 text-slate-500 hover:bg-white/5"
                            >
                              <Star className={cn("h-3.5 w-3.5 transition-colors", file.favorite ? "fill-amber-400 text-amber-400" : "text-slate-500 hover:text-slate-300")} />
                            </button>
                          )}

                          {/* Options/Trash */}
                          {activeNav === 'trash' ? (
                            <div className="flex gap-1">
                              <button 
                                title="Restaurar archivo"
                                onClick={(e) => restoreFromTrash(file, e)}
                                className="rounded-lg p-1 text-indigo-400 hover:bg-indigo-500/10"
                              >
                                <Check className="h-3.5 w-3.5" />
                              </button>
                              <button 
                                title="Eliminar permanentemente"
                                onClick={(e) => deletePermanently(file.id, e)}
                                className="rounded-lg p-1 text-rose-400 hover:bg-rose-500/10"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          ) : (
                            <button 
                              onClick={(e) => moveToTrash(file, e)}
                              title="Mover a papelera"
                              className="rounded-lg p-1 text-slate-500 hover:text-rose-400 hover:bg-rose-500/5"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </button>
                          )}
                        </div>
                      </div>

                      {/* File Info */}
                      <div className="mt-4 leading-normal relative z-10">
                        <h4 className="truncate text-xs font-semibold text-white group-hover:text-indigo-400 transition-colors" title={file.name}>
                          {file.name}
                        </h4>
                        <div className="mt-1 flex items-center gap-1.5 text-[9px] text-slate-400 font-mono">
                          <span>{file.size}</span>
                          <span>•</span>
                          <span>{file.date}</span>
                        </div>
                      </div>

                      {/* Bento Absolute Highlight Border gradient */}
                      <div className="absolute inset-0 -z-10 rounded-xl p-px bg-gradient-to-br from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
                    </div>
                  );
                })}
              </div>
            )}
          </div>

        </div>

      </main>

      {/* UPGRADE PLAN GLASSMORPHISM MODAL */}
      {isUpgradeOpen && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-[#06080F]/80 backdrop-blur-md p-5 animate-in fade-in duration-300">
          <GlowCard
            customSize={true}
            glowColor="blue"
            className="w-[min(540px,100%)] p-6 bg-[#0F131E] border border-white/[0.08] shadow-[0_30px_90px_rgba(0,0,0,0.65)] animate-in scale-in duration-300"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-white/[0.05] pb-4 text-left">
              <div className="flex items-center gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-indigo-500/10 text-[#6366F1]">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Upgrade Your Storage</h3>
                  <p className="text-xs text-slate-400">Expande tu capacidad de renderizado hoy mismo</p>
                </div>
              </div>
              <button 
                onClick={() => setIsUpgradeOpen(false)}
                className="rounded-lg border border-white/[0.06] bg-[#0F131E] p-1.5 text-slate-400 hover:text-white hover:bg-[#151A23]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Modal Plans */}
            <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
              
              {/* Plan 1 */}
              <div className="group relative rounded-xl border border-white/[0.08] bg-[#151A23]/50 p-4 text-left hover:border-white/[0.12] transition-all duration-300 hover:shadow-[0_2px_12px_rgba(255,255,255,0.02)] hover:-translate-y-0.5 will-change-transform overflow-hidden">
                {/* Bento Absolute Background dots */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[length:4px_4px]" />
                </div>

                <span className="text-[10px] font-bold uppercase tracking-wider text-[#6366F1] z-10 relative">Standard Plan</span>
                <h4 className="mt-2 font-display text-2xl font-bold text-white z-10 relative">$5<span className="text-xs text-slate-400">/mo</span></h4>
                <p className="mt-1 text-[11px] text-slate-400 z-10 relative">Adecuado para renderizadores independientes.</p>
                
                <div className="mt-4 space-y-2 text-[10px] text-slate-300 z-10 relative">
                  <div className="flex items-center gap-2">
                    <Check className="h-3 w-3 text-emerald-400" />
                    <span>250 GB Storage Space</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-3 w-3 text-emerald-400" />
                    <span>Renderings up to 2K</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-3 w-3 text-emerald-400" />
                    <span>2 Concurrent Jobs</span>
                  </div>
                </div>

                <button 
                  onClick={() => { setIsUpgradeOpen(false); showToast('Plan Standard seleccionado.'); }}
                  className="mt-6 w-full relative z-10 rounded-lg bg-white/5 py-2 text-xs font-semibold text-white hover:bg-white/10 active:bg-white/15 border border-white/[0.08]"
                >
                  Choose Standard
                </button>

                {/* Bento Absolute Highlight Border gradient */}
                <div className="absolute inset-0 -z-10 rounded-xl p-px bg-gradient-to-br from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
              </div>

              {/* Plan 2 Premium */}
              <div className="group relative rounded-xl border border-indigo-500/30 bg-indigo-950/20 p-4 text-left shadow-[0_4px_30px_rgba(99,102,241,0.1)] hover:border-indigo-500/50 transition-all duration-300 hover:shadow-[0_2px_12px_rgba(99,102,241,0.2)] hover:-translate-y-0.5 will-change-transform overflow-hidden">
                {/* Bento Absolute Background dots */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.04)_1px,transparent_1px)] bg-[length:4px_4px]" />
                </div>

                <span className="absolute top-3 right-3 rounded-full bg-indigo-500/20 px-2 py-0.5 text-[8px] font-bold text-[#818CF8] z-10">POPULAR</span>
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#A855F7] z-10 relative">Ultimate Pro</span>
                <h4 className="mt-2 font-display text-2xl font-bold text-white z-10 relative">$12<span className="text-xs text-slate-400">/mo</span></h4>
                <p className="mt-1 text-[11px] text-slate-400 z-10 relative">El poder ilimitado para estudios y agencias.</p>
                
                <div className="mt-4 space-y-2 text-[10px] text-slate-300 z-10 relative">
                  <div className="flex items-center gap-2">
                    <Check className="h-3 w-3 text-[#A855F7]" />
                    <span>1 TB Storage Space</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-3 w-3 text-[#A855F7]" />
                    <span>Renderings in 4K UHD</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-3 w-3 text-[#A855F7]" />
                    <span>8 Concurrent Jobs</span>
                  </div>
                </div>

                <button 
                  onClick={() => { setIsUpgradeOpen(false); showToast('Suscrito a Ultimate Pro exitosamente.'); }}
                  className="mt-6 w-full relative z-10 rounded-lg bg-indigo-600 py-2 text-xs font-semibold text-white hover:bg-indigo-500 active:bg-indigo-700 shadow-md"
                >
                  Choose Ultimate Pro
                </button>

                {/* Bento Absolute Highlight Border gradient */}
                <div className="absolute inset-0 -z-10 rounded-xl p-px bg-gradient-to-br from-transparent via-indigo-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
              </div>

            </div>

            {/* Terms */}
            <p className="mt-5 text-[10px] text-slate-500 text-center">
              Al suscribirte aceptas los términos y condiciones del servicio de ManimStudio.
            </p>
          </GlowCard>
        </div>
      )}

    </div>
  );
}

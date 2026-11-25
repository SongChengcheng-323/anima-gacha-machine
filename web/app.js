const $ = s => document.querySelector(s);
let STATE = {char:'', chars:'', style:'', tier:'', ratio:'', album:'', sort:'new', tag:'', fav:'', tagExpanded:false};
let ALL = [];
let CUR = null;
let SEL = new Set();
let SELMODE = false;

async function api(p){ return (await fetch(p)).json(); }
async function post(p, body){
  return (await fetch(p, {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify(body)})).json();
}
function toast(msg){
  const t = $('#toast'); t.textContent = msg; t.classList.add('show');
  clearTimeout(window.__tt); window.__tt = setTimeout(()=>t.classList.remove('show'), 1800);
}

const PERSIST_KEYS = ['char','chars','style','tier','album','sort','tag','fav'];
function saveState(){
  try{ localStorage.setItem('xa_state', JSON.stringify(STATE)); }catch(e){}
  try{
    const u = new URL(location.href);
    PERSIST_KEYS.forEach(k => { const v = STATE[k]; if(v) u.searchParams.set(k, v); else u.searchParams.delete(k); });
    history.replaceState(null, '', u.toString());
  }catch(e){}
}
function restoreState(){
  try{
    const p = new URLSearchParams(location.search);
    let fromUrl = false;
    PERSIST_KEYS.forEach(k => { if(p.has(k)){ STATE[k] = p.get(k); fromUrl = true; } });
    if(!fromUrl){
      const s = JSON.parse(localStorage.getItem('xa_state') || '{}');
      PERSIST_KEYS.forEach(k => { if(s[k] !== undefined && s[k] !== null) STATE[k] = s[k]; });
    }
    if(STATE.chars) CHAR_SEL = new Set(STATE.chars.split(',').filter(Boolean));
  }catch(e){}
}
function saveView(rel){

  const name = rel ? String(rel).split('/').pop() : '';
  try{ localStorage.setItem('xa_view', name); }catch(e){}
  try{
    const u = new URL(location.href);
    if(name) u.searchParams.set('view', name); else u.searchParams.delete('view');
    history.replaceState(null, '', u.toString());
  }catch(e){}
}

async function restoreView(){
  let rel = null;
  try{ rel = new URLSearchParams(location.search).get('view'); }catch(e){}
  if(!rel){ try{ rel = localStorage.getItem('xa_view') || null; }catch(e){} }
  if(!rel) return;
  for(let i = 0; i < 20; i++){

    const idx = ALL.findIndex(p => p.rel === rel || p.name === rel);
    if(idx >= 0){ openViewer(idx); return; }
    if(!window.__hasMore) break;
    await fetchPage(false);
  }
}
async function boot(){
  await ensureTaglib();                 
  restoreState();                       
  const facets = await api('/api/facets');
  window.__facets = facets;      
  renderCharChips(facets);
  renderTagChips(facets.tags || []);
  $('#f-style').innerHTML = '<option value="">全部画风</option>' +
    facets.styles.map(([k,n]) => `<option value="${k}">${styleCN(k)} (${n})</option>`).join('');

  $('#f-work').innerHTML = '<option value="">全部作品</option>' +
    (facets.works || []).map(([k, cn, n]) => `<option value="${k}">${cn || k} (${n})</option>`).join('');
  $('#f-album').innerHTML = '<option value="">全部相册</option>' +
    facets.albums.map(([k,n]) => `<option value="${k}">${k} (${n})</option>`).join('');

  renderTierFilterOptions();            
  $('#f-style').value = STATE.style || '';
  $('#f-tier').value = STATE.tier || '';
  if($('#f-ratio')) $('#f-ratio').value = STATE.ratio || '';
  $('#f-work').value = STATE.work || '';
  $('#f-album').value = STATE.album || '';
  $('#f-sort').value = STATE.sort || 'new';
  $('#btn-fav').classList.toggle('on', STATE.fav === '1');
  ['f-style','f-tier','f-ratio','f-work','f-album','f-sort'].forEach(id => $('#'+id).onchange = () => {
    STATE.style = $('#f-style').value; STATE.tier = $('#f-tier').value;
    STATE.ratio = $('#f-ratio').value;
    STATE.work = $('#f-work').value; STATE.album = $('#f-album').value;
    STATE.sort = $('#f-sort').value; load();
  });
  $('#btn-fav').onclick = () => {
    STATE.fav = STATE.fav === '1' ? '' : '1';
    $('#btn-fav').classList.toggle('on', STATE.fav === '1');
    load();
  };
  $('#btn-sel').onclick = () => toggleSelMode();
  await load(); await loadAlbums();
  loadVersion();                        
  restoreView();                        
  resumeRedraw();                       

  try{
    const sy = parseInt(sessionStorage.getItem('xa_scroll') || '0', 10);
    const hasView = new URLSearchParams(location.search).get('view') || localStorage.getItem('xa_view');
    if(sy > 0 && !hasView){

      [150, 500, 1200].forEach(d => setTimeout(() => window.scrollTo(0, sy), d));
    }
  }catch(e){}
}

(function(){
  window.__xaProgScrollUntil = 0;
  const mark = () => { window.__xaProgScrollUntil = performance.now() + 500; };
  const _st = window.scrollTo ? window.scrollTo.bind(window) : null;
  if(_st) window.scrollTo = function(){ mark(); return _st.apply(window, arguments); };
  const _si = Element.prototype.scrollIntoView;
  Element.prototype.scrollIntoView = function(){ mark(); return _si.apply(this, arguments); };
})();

(function(){
  let lastY = window.scrollY, acc = 0, collapsed = false, locked = false;
  const hdr = document.querySelector('header');
  if(!hdr) return;
  const TOP = 10;              
  const TH  = 60;              
  const MIN_ROOM = 260;        
  const scrollRoom = () => Math.max(0,
        document.documentElement.scrollHeight - window.innerHeight);

  const chipsOpen = () => (typeof CHAR_EXPANDED !== 'undefined' && CHAR_EXPANDED)
        || (typeof STATE !== 'undefined' && STATE && STATE.tagExpanded);
  const progScrolling = () => window.__xaProgScrollUntil
        && performance.now() < window.__xaProgScrollUntil;

  window.addEventListener('scroll', () => {
    const y = window.scrollY, dy = y - lastY;
    lastY = y;
    if(chipsOpen()){ acc = 0; return; }          
    if(progScrolling()){ acc = 0; return; }      
    if(locked){

      if(scrollRoom() > MIN_ROOM + 260) locked = false;
      else return;
    }
    if(y <= TOP){                                   
      if(collapsed){
        collapsed = false; hdr.classList.remove('collapsed');
        if(scrollRoom() < MIN_ROOM) locked = true;  
      }
      acc = 0;
      return;
    }
    if(collapsed) return;
    if(dy > 0) acc += dy; else acc = 0;
    if(acc > TH){

      if(scrollRoom() < MIN_ROOM + 220){ locked = true; return; }
      collapsed = true; hdr.classList.add('collapsed');
    }
  }, {passive: true});
})();

(function(){
  const b = document.getElementById('to-top');
  if(!b) return;
  window.addEventListener('scroll', () => {
    b.classList.toggle('show', window.scrollY > 400);
  }, {passive: true});
})();

function syncMergeBtn(){
  const btn = document.getElementById('btn-merge');
  const sel = document.getElementById('f-album');
  if(!btn || !sel) return;
  const v = sel.value || '';
  const ok = /^重抽_\d{8}$/.test(v);
  btn.style.display = ok ? '' : 'none';
  btn.dataset.album = ok ? v : '';
}
document.addEventListener('change', e => {
  if(e.target && e.target.id === 'f-album') syncMergeBtn();
});

[300, 1000, 2500].forEach(d => setTimeout(syncMergeBtn, d));
async function mergeRedrawFolder(){
  const btn = document.getElementById('btn-merge');
  const album = btn && btn.dataset.album;
  if(!album) return;
  const date = album.replace(/^重抽_/, '');
  if(!confirm(`把「${album}」里的图全部搬进「${date}」？\n\n`
            + `· 目标日期按文件夹名对应 → ${date}/\n`
            + `· 搬完删除 ${album}/（下次重抽会重新生成）\n`
            + `· 遇到同名文件不覆盖，自动加 _1 后缀`)) return;
  btn.disabled = true; btn.textContent = '📥 搬运中…';
  try{
    const r = await post('/api/merge-redraw', {album});
    if(r.ok){
      toast(`✅ 已合并 ${r.moved} 张 → ${r.target}/`
            + (r.renamed && r.renamed.length ? `（${r.renamed.length} 张重名已改名）` : ''));
      STATE.album = '';                      
      const sel = document.getElementById('f-album');
      if(sel) sel.value = '';
      await load();
      if(typeof loadAlbums === 'function') await loadAlbums();
    } else {
      alert('合并未完成：' + (r.error || '未知错误'));
    }
  }catch(e){ alert('合并失败：' + e); }
  btn.disabled = false; btn.textContent = '📥 一键合并入当天';
  syncMergeBtn();
}

let GRID_TARGET = 200;        
function layoutGrid(){
  const g = document.getElementById('grid');
  if(!g) return;
  const w = g.clientWidth || document.documentElement.clientWidth || window.innerWidth || 1200;
  const cols = Math.max(2, Math.round(w / GRID_TARGET));
  const cur = document.documentElement.style.getPropertyValue('--cols');
  if(cur !== String(cols)){
    document.documentElement.style.setProperty('--cols', cols);
  }
}
window.addEventListener('resize', layoutGrid);
window.addEventListener('orientationchange', () => setTimeout(layoutGrid, 120));
setTimeout(layoutGrid, 0);

let CHAR_ALL = [];
let CHAR_SEL = new Set();       
let CHAR_EXPANDED = false;

function syncHdrChipsOpen(){
  const hdr = document.querySelector('#page-photos header');
  if(!hdr) return;
  hdr.classList.toggle('chips-open',
        !!(CHAR_EXPANDED || (typeof STATE !== 'undefined' && STATE && STATE.tagExpanded)));
}

function renderCharChips(facets){
  CHAR_ALL = facets.chars || [];                  
  syncHdrChipsOpen();                             
  const fc = $('#f-char');
  const MAX = CHAR_EXPANDED ? 999 : 14;           
  const show = CHAR_ALL.slice(0, MAX);
  fc.innerHTML =
    `<div class="chip${CHAR_SEL.size===0?' on':''}" data-k="">全部角色</div>` +
    show.map(([k, n]) =>
      `<div class="chip${CHAR_SEL.has(k)?' on':''}" data-k="${k}">${short(k)} <b style="opacity:.6">${n}</b></div>`
    ).join('');

  const TOGGLE_BASE = 14;
  const tog = $('#char-toggle');
  if(CHAR_ALL.length > TOGGLE_BASE){
    tog.style.display = 'block';
    tog.textContent = CHAR_EXPANDED ? '收起 ▲' : `展开全部 ${CHAR_ALL.length} 个 ▼`;
    tog.onclick = () => { CHAR_EXPANDED = !CHAR_EXPANDED; renderCharChips(facets); };
  } else {
    tog.style.display = 'none';
  }
  fc.classList.toggle('expanded', !!CHAR_EXPANDED);
  fc.style.maxHeight = CHAR_EXPANDED ? 'none' : '76px';
  fc.onclick = e => {
    const c = e.target.closest('.chip'); if(!c) return;
    const k = c.dataset.k;
    if(k === ''){ CHAR_SEL.clear(); }                 
    else if(CHAR_SEL.has(k)){ CHAR_SEL.delete(k); }
    else { CHAR_SEL.add(k); }
    STATE.chars = [...CHAR_SEL].join(',');
    renderCharChips(facets);
    load();
  };
}

function renderTagChips(tags){
  const ft = $('#f-tag');
  const wrap = document.getElementById('tag-wrap');
  if(wrap) wrap.style.display = 'block';           
  syncHdrChipsOpen();                             
  if(!tags.length){
    ft.innerHTML = '<div class="chip" style="opacity:.45;cursor:default">🏷 暂无标签（在图上打标签后会出现在这里）</div>';
    return;
  }
  ft.style.display = 'flex';
  ft.classList.toggle('expanded', !!STATE.tagExpanded);
  ft.style.maxHeight = STATE.tagExpanded ? 'none' : '76px';
  const MAX = STATE.tagExpanded ? 999 : 7;          
  const show = STATE.tagExpanded ? tags : tags.slice(0, MAX);
  ft.innerHTML = '<div class="chip' + (STATE.tag===''?' on':'') + '" data-v="">全部标签</div>' +
    show.map(([k,n]) => `<div class="chip${STATE.tag===k?' on':''}" data-v="${k}">🏷 ${k} <b style="opacity:.6">${n}</b></div>`).join('');

  const ttg = $('#tag-toggle');

  const TAG_TOGGLE_BASE = 7;
  if(tags.length > TAG_TOGGLE_BASE){
    ttg.style.display = 'block';
    ttg.textContent = STATE.tagExpanded ? '收起 ▲' : `展开全部 ${tags.length} 个 ▼`;
    ttg.onclick = () => { STATE.tagExpanded = !STATE.tagExpanded; renderTagChips(tags); };
  } else {
    ttg.style.display = 'none';
  }
  ft.onclick = e => {
    const c = e.target.closest('.chip'); if(!c) return;
    ft.querySelectorAll('.chip').forEach(x=>x.classList.remove('on')); c.classList.add('on');
    STATE.tag = c.dataset.v; load();
  };
}

const SHORT_CN = {"菈菈·萨塔琳·戴比路克":"菈菈", "喜多川海梦":"海梦",
                  "阿尔托莉雅·潘德拉贡":"Saber", "惣流·明日香·兰格雷":"明日香",
                  "结城明日奈":"亚丝娜", "碧蓝航线:圣路易斯":"圣路易斯"};
function short(s){
  const cn = (TAGLIB.cn && TAGLIB.cn[s]) || composeCN(s) || s;
  return SHORT_CN[cn] || cn.replace(/_\(.*?\)/,'').replace(/_/g,' ');
}

const _byLen = tb => Object.keys(tb || {}).sort((a, b) => b.length - a.length);
function _stripPre(s, tb){
  for(const k of _byLen(tb)){
    if(s === k) return [tb[k], ''];
    if(s.startsWith(k + ' ')) return [tb[k], s.slice(k.length + 1)];
  }
  return [null, s];
}
function _stripTail(s, tb){
  for(const k of _byLen(tb)){
    if(s === k) return [tb[k], ''];
    if(s.endsWith(' ' + k)) return [tb[k], s.slice(0, -(k.length + 1))];
  }
  return [null, s];
}
function composeCN(en){
  const C = TAGLIB.compose;
  if(!C || !C.ITEM) return null;
  let s = String(en || '').trim().toLowerCase();
  if(!s) return null;
  let head = '';
  if(s.startsWith('a pair of ')){ head = '一双'; s = s.slice(10); }
  const pre = [], post = [];
  for(let i = 0; i < 3; i++){ const [p, s2] = _stripTail(s, C.POST); if(p && s2 !== s){ post.unshift(p); s = s2; } else break; }
  for(let i = 0; i < 3; i++){ const [p, s2] = _stripTail(s, C.PRE);  if(p && s2 !== s){ pre.unshift(p);  s = s2; } else break; }
  const adjs = [];
  for(let i = 0; i < 5; i++){
    let [p, s2] = _stripPre(s, C.PRE);
    if(p && s2 !== s){ pre.push(p); s = s2; continue; }
    [p, s2] = _stripPre(s, C.COLOR);
    if(p && s2 !== s){ adjs.push(p); s = s2; continue; }
    break;
  }
  const item = C.ITEM[s];
  if(!item) return null;
  if(!(adjs.length || pre.length || post.length || head)) return null;
  return head + pre.join('') + adjs.join('') + item + post.join('');
}
function styleCN(s){ return ({flat:'平涂',painterly:'厚涂',oil:'油画',realistic:'写实'})[s]||s; }
function tierCN(t){ return ({fashion:'✨ 时尚',tease:'擦边',exposed:'暴露',sex:'🔥 性爱',normal:'日常',unknown:'未知'})[t]||t||'未知'; }
function tierCls(t){ return ({exposed:'exp',sex:'sex',fashion:'fashion',normal:'normal',tease:'tease'})[t]||''; }

const POS_CN = {missionary:'传教士',doggystyle:'后入',cowgirl:'女上',reverse_cowgirl:'反向女上',
  spooning:'侧入',standing_wall:'站立',mating_press:'压制位',fellatio:'口交',paizuri:'乳交',
  cunnilingus:'舔阴',footjob:'足交',anal:'肛交',handjob:'手交',tribadism:'磨镜',
  masturbation:'前戏',toy:'玩具',69:'69',sex:'性爱',normal:''};
function posCN(a){ return POS_CN[a]||''; }

async function load(){
  saveState();                          
  $('#loading').style.display='block';
  STATE.offset = 0;
  await fetchPage(true);
  $('#loading').style.display='none';
}

async function fetchPage(reset){
  const PAGE = 60;
  const q = new URLSearchParams(STATE).toString() + `&limit=${PAGE}&offset=${STATE.offset||0}`;
  const d = await api('/api/photos?'+q);

  if(reset){ ALL = []; try{ _imgObs.disconnect(); }catch(e){} $('#grid').innerHTML=''; }
  ALL = ALL.concat(d.photos);
  $('#cnt').textContent = `(${ALL.length}/${d.total})`;
  const more = d.photos.map((p) => {
    const i = ALL.length - d.photos.length + d.photos.indexOf(p);
    return `<div class="ph${SEL.has(p.rel)?' sel':''}" data-rel="${p.rel}" data-i="${i}" onclick="clickPhoto(${i},event)">
       <img src="/img?p=${encodeURIComponent(p.rel)}&t=thumb&v=${Math.round(p.mtime||0)}" loading="lazy">
       <span class="badge ${tierCls(p.tier)}" title="点击指定角色"
             onclick="event.stopPropagation();openCharPicker(${i})"
             style="cursor:pointer">${short(p.char)}${p.char_manual ? '*' : ''}</span>
       ${(p.vcount||1)>1?`<span class="vbadge" title="${p.vcount} 个版本（大图里左右滑动切换）">${p.vcount}</span>`:''}
       ${p.fav?'<span class="favstar">⭐</span>':''}
       <!-- ⛔ 2026-10-12：「体位识别不对，我觉得可以不要那个右下角的徽章了」⇒ 摘掉 ✓ -->
       <!-- 原：${p.tier==='sex'&&posCN(p.action)?`<span class="posbadge">${posCN(p.action)}</span>`:''} -->
       ${p.tags&&p.tags.length?'<span class="badge" style="left:3px;top:20px;background:rgba(60,90,200,.85)">🏷'+p.tags.length+'</span>':''}
     </div>`;
  }).join('');
  $('#grid').insertAdjacentHTML('beforeend', more);
  watchGridImages();
  $('#grid').className = SELMODE ? 'selmode' : '';
  STATE.offset = (STATE.offset||0) + d.photos.length;
  window.__hasMore = STATE.offset < d.total;
  updateSelBar();
}

const LAZY_GAP = 2500;
const _imgObs = new IntersectionObserver((es) => {
  for (const e of es) {
    const img = e.target;
    if (e.isIntersecting) {
      if (img.dataset.real) { img.src = img.dataset.real; delete img.dataset.real; }
    } else if (img.getAttribute('src')) {
      img.dataset.real = img.getAttribute('src');
      img.removeAttribute('src');
    }
  }
}, { rootMargin: LAZY_GAP + 'px 0px ' + LAZY_GAP + 'px 0px' });

function watchGridImages(){
  document.querySelectorAll('#grid .ph img').forEach(img => {
    if (!img.dataset.watched) { img.dataset.watched = '1'; _imgObs.observe(img); }
  });
}

const PAGE_T0 = Date.now();
setInterval(() => {
  if (window.__slowWarned) return;
  const m = Math.round((Date.now() - PAGE_T0) / 60000);
  if (m >= 60 && !document.hidden) { window.__slowWarned = true; showSlowBar(m); }
}, 60000);

function showSlowBar(m){
  if (document.getElementById('slowbar')) return;
  const b = document.createElement('div');
  b.id = 'slowbar';
  b.innerHTML = '<span>相册已经开着 ' + m + ' 分钟了，滚过的图会占着内存</span>' +
                '<button>刷新回收</button><button class="x">×</button>';
  Object.assign(b.style, {position:'fixed',left:'50%',top:'10px',transform:'translateX(-50%)',
    zIndex:9999,display:'flex',gap:'8px',alignItems:'center',padding:'8px 12px',
    background:'rgba(40,30,60,.95)',border:'1px solid rgba(255,255,255,.18)',
    borderRadius:'10px',fontSize:'12px',color:'#eee',boxShadow:'0 6px 20px rgba(0,0,0,.45)'});
  b.querySelector('button').onclick = () => location.reload();
  b.querySelector('.x').onclick = () => b.remove();
  document.body.appendChild(b);
}

document.addEventListener('visibilitychange', () => {
  if (document.hidden) { window.__hiddenAt = Date.now(); return; }
  if (window.__hiddenAt && Date.now() - window.__hiddenAt > 10 * 60 * 1000) {
    document.querySelectorAll('#grid .ph img[src]').forEach(img => {
      if (!img.dataset.real) {
        img.dataset.real = img.getAttribute('src');
        img.removeAttribute('src');
      }
    });
  }
  window.__hiddenAt = 0;
});

let _loadingMore = false;
window.addEventListener('scroll', () => {
  try{ sessionStorage.setItem('xa_scroll', String(Math.round(window.scrollY))); }catch(e){}
}, {passive:true});
window.addEventListener('scroll', async () => {
  if(_loadingMore || !window.__hasMore) return;
  const nearBottom = window.innerHeight + window.scrollY > document.body.scrollHeight - 900;
  if(!nearBottom) return;
  _loadingMore = true;
  const hint = $('#loading'); hint.textContent='加载更多…'; hint.style.display='block';
  await fetchPage(false);
  hint.style.display='none';
  _loadingMore = false;
}, {passive:true});

function exitSelMode(){
  SEL.clear(); SELMODE = false;
  $('#btn-sel').textContent = '选择'; $('#btn-sel').classList.remove('on');
  const b = $('#btn-allsel'); if(b) b.textContent = '☑ 全选';    
  $('#grid').className = '';
  syncSelClasses();                 
  updateSelBar();
}
function toggleSelMode(){
  if(SELMODE){ exitSelMode(); return; }        
  SELMODE = true; SEL.clear();
  $('#btn-sel').textContent = '完成'; $('#btn-sel').classList.add('on');
  const b = $('#btn-allsel'); if(b) b.textContent = '☑ 全选';
  $('#grid').className = 'selmode';
  syncSelClasses();
  updateSelBar();
}

let CM_RELS = [];

function openCharPicker(i){
  const p = ALL[i];
  if(!p) return;
  CM_RELS = (SELMODE && SEL.size) ? [...SEL] : [p.rel];
  showCharModal();
}
function openCharPickerForSel(){
  if(!SEL.size){ toast('先点选图片'); return; }
  CM_RELS = [...SEL];
  showCharModal();
}
function showCharModal(){
  $('#charmodal').classList.add('show');
  const inp = $('#cm-search'); if(inp) inp.value = '';
  $('#cm-n').textContent = CM_RELS.length > 1 ? `（${CM_RELS.length} 张）` : '';
  renderTierRow();          
  renderCharList();
}
function closeCharPicker(){ $('#charmodal').classList.remove('show'); }
function renderCharList(){
  const kw = (($('#cm-search').value) || '').trim().toLowerCase();
  const chars = (window.__facets && window.__facets.chars) || [];
  const list = chars
    .map(([k, n]) => [k, short(k), n])
    .filter(([k, cn, n]) => !kw || k.toLowerCase().includes(kw) || (cn || '').toLowerCase().includes(kw));
  CM_NEW = cmNewName();
  let html = '';
  if(CM_NEW){
    const esc = CM_NEW.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    html += `<div class="cm-item cm-new" onclick="createCharNew()">＋ 新建角色「${esc}」</div>`;
  }
  html += list.length
    ? list.map(([k, cn, n]) =>
        `<div class="cm-item" onclick="pickChar('${k}')">${cn} <b style="opacity:.5">${n}</b></div>`).join('')
    : (CM_NEW ? '' : '<div style="color:var(--fg2);font-size:13px;padding:14px">没有匹配的角色</div>');
  $('#cm-list').innerHTML = html;
}

let CM_NEW = '';
function cmNorm(s){ return (s || '').toLowerCase().replace(/[\s_]+/g, ''); }
function cmNewName(){
  const raw = (($('#cm-search').value) || '').trim();
  if(!raw) return '';
  const chars = (window.__facets && window.__facets.chars) || [];
  return chars.some(([k]) => cmNorm(k) === cmNorm(raw)) ? '' : raw;
}
function createCharNew(){ if(CM_NEW) createChar(CM_NEW); }
async function createChar(name){
  name = (name || '').trim();
  if(!name || !CM_RELS.length) return;
  try{
    const r = await post('/api/char', {paths: CM_RELS, char: name});
    toast(`✅ 已新建并指定「${name}」（${r.affected} 张）`);
  }catch(e){ alert('指定失败：' + e); return; }
  closeCharPicker();

  try{ window.__facets = await api('/api/facets'); renderCharChips(window.__facets); }catch(e){}
  await load();
}
async function pickChar(tag){
  if(!CM_RELS.length) return;
  try{
    const r = await post('/api/char', {paths: CM_RELS, char: tag});
    toast(tag ? `✅ 已指定为「${short(tag)}」（${r.affected} 张）`
              : `✅ 已清除指定，回到自动识别（${r.affected} 张）`);
  }catch(e){ alert('指定失败：' + e); return; }
  closeCharPicker();
  await load();        
}

let TM_RELS = [];
const TIER_LIST = [
  ["normal",  "普通",   "rgba(245,245,250,.92)"],
  ["fashion", "✨ 时尚", "rgba(90,140,240,.85)"],
  ["tease",   "擦边",   "rgba(190,150,80,.85)"],
  ["exposed", "暴露",   "rgba(220,50,110,.85)"],
  ["sex",     "🔥 性爱", "linear-gradient(135deg,#ff2e63,#a4133c)"],
];
function tierLabel(t){ const x = TIER_LIST.find(v => v[0] === t); return x ? x[1] : (t || '未知'); }

const TIER_PICK = TIER_LIST;

const TIER_FILTER = [["takeoff", "✈️ 起飞", "linear-gradient(135deg,#ff9a3c,#ff2e63)"], ...TIER_PICK];

function renderTierFilterOptions(){
  const sel = $('#f-tier'); if(!sel) return;
  sel.innerHTML = '<option value="">全部尺度</option>' +
    TIER_FILTER.map(([k, cn]) => `<option value="${k}">${cn}</option>`).join('');
}

function renderTierRow(){
  const box = $('#cm-tiers'); if(!box) return;
  box.innerHTML = '<span class="cap">尺度</span>' + TIER_PICK.map(([k, cn, bg]) =>
    `<span class="tchip" style="--c:${bg}" onclick="pickTierForRels('${k}')">${cn}</span>`).join('');
}
async function pickTierForRels(t){
  if(!CM_RELS.length) return;
  try{
    const r = await post('/api/tier', {paths: CM_RELS, tier: t});

    if(r && r.error){ alert('设置失败：' + r.error); return; }
    toast(`✅ 已设为「${tierLabel(t)}」（${r.affected} 张）`);
  }catch(e){ alert('指定失败：' + e); return; }
  closeCharPicker();
  await load();
}
function openTierPickerForSel(){
  if(!SEL.size){ toast('先点选图片'); return; }
  TM_RELS = [...SEL];
  showTierModal();
}
function showTierModal(){
  $('#tiermodal').classList.add('show');
  $('#tm2-n').textContent = TM_RELS.length > 1 ? `（${TM_RELS.length} 张）` : '';
  $('#tm2-list').innerHTML = TIER_PICK.map(([k, cn, bg]) =>
    `<div class="tm-row" onclick="pickTier('${k}')">
       <span class="sw" style="background:${bg}"></span>${cn}
     </div>`).join('');
}
function closeTierPicker(){ $('#tiermodal').classList.remove('show'); }
async function pickTier(t){
  if(!TM_RELS.length) return;
  try{
    const r = await post('/api/tier', {paths: TM_RELS, tier: t});
    if(r && r.error){ alert('设置失败：' + r.error); return; }
    toast(t ? `✅ 已设为「${tierLabel(t)}」（${r.affected} 张）`
            : `✅ 已清除分类指定（${r.affected} 张）`);
  }catch(e){ alert('指定失败：' + e); return; }
  closeTierPicker();
  await load();
}

async function clickPhoto(i, ev){

  if(_DRAG_SKIP && Date.now() - _DRAG_SKIP < 500) return;

  if(!SELMODE){ openViewer(i); return; }
  const p = ALL[i];
  if(!p) return;
  const rel = p.rel;
  if(SEL.has(rel)) SEL.delete(rel); else SEL.add(rel);

  const nodes = document.querySelectorAll('#grid .ph');
  if(nodes[i]) nodes[i].classList.toggle('sel', SEL.has(rel));
  updateSelBar();
}

let _DRAG = null, _DRAG_SKIP = 0, _autoScrollRAF = 0;
const DRAG_TRIGGER = 10;     
const DRAG_RATIO   = 1.5;    
const SCROLL_EDGE  = 60;     
const SCROLL_BASE  = 3;      

function _phAt(x, y){
  const el = document.elementFromPoint(x, y);
  const ph = el && el.closest && el.closest('#grid .ph');
  if(!ph) return -1;
  const n = parseInt(ph.dataset.i, 10);
  return isNaN(n) ? -1 : n;
}

function _selApply(i, on){
  const p = ALL[i]; if(!p) return;
  if(on){ if(SEL.has(p.rel)) return; SEL.add(p.rel); }
  else  { if(!SEL.has(p.rel)) return; SEL.delete(p.rel); }
  const ph = document.querySelector(`#grid .ph[data-i="${i}"]`);
  if(ph) ph.classList.toggle('sel', on);
}

function _applyRange(startI, curI, on){
  if(!_DRAG) return;
  const nMin = Math.min(startI, curI), nMax = Math.max(startI, curI);
  const oMin = Math.min(startI, _DRAG.lastI), oMax = Math.max(startI, _DRAG.lastI);
  if(nMin === oMin && nMax === oMax) return;
  for(let i = oMin; i <= oMax; i++) if(i < nMin || i > nMax) _selApply(i, !on);
  for(let i = nMin; i <= nMax; i++) if(i < oMin || i > oMax) _selApply(i, on);
  _DRAG.lastI = curI;
  updateSelBar();
}

function _gridBottom(){
  const bar = document.getElementById('selbar');
  if(bar && bar.classList.contains('show')){
    const r = bar.getBoundingClientRect();
    if(r.height > 0) return Math.min(window.innerHeight, r.top);
  }
  return window.innerHeight;
}

function _autoScrollStep(){
  if(!_DRAG || !_DRAG.applied){ _autoScrollRAF = 0; return; }
  const y  = _DRAG.cy;
  const H  = _gridBottom();
  let v = 0;
  if(y < SCROLL_EDGE){
    const f = (SCROLL_EDGE - y) / SCROLL_EDGE;              
    v = -(SCROLL_BASE + f * SCROLL_BASE * 3);
  } else if(y > H - SCROLL_EDGE){
    const f = Math.min(1, (y - (H - SCROLL_EDGE)) / SCROLL_EDGE);
    v =  (SCROLL_BASE + f * SCROLL_BASE * 3);
  }
  if(!v){ _autoScrollRAF = 0; return; }
  const before = window.scrollY;
  window.scrollBy(0, v);
  if(window.scrollY === before){ _autoScrollRAF = 0; return; }   

  const i = _phAt(_DRAG.cx, Math.min(y, H - 8));
  if(i >= 0) _applyRange(_DRAG.i0, i, _DRAG.add);
  _autoScrollRAF = requestAnimationFrame(_autoScrollStep);
}

document.addEventListener('pointerdown', ev => {
  if(!SELMODE || ev.button > 0) return;
  const ph = ev.target.closest && ev.target.closest('#grid .ph');
  if(!ph) return;
  const i = _phAt(ev.clientX, ev.clientY);
  if(i < 0 || !ALL[i]) return;
  _DRAG = {i0:i, add: !SEL.has(ALL[i].rel), applied:false, aborted:false, lastI:i,
           sx:ev.clientX, sy:ev.clientY, cx:ev.clientX, cy:ev.clientY};
}, true);

document.addEventListener('pointermove', ev => {
  if(!_DRAG || _DRAG.aborted) return;
  _DRAG.cx = ev.clientX; _DRAG.cy = ev.clientY;

  if(!_DRAG.applied){
    const ax = Math.abs(ev.clientX - _DRAG.sx), ay = Math.abs(ev.clientY - _DRAG.sy);
    if(ax < DRAG_TRIGGER && ay < DRAG_TRIGGER) return;

    if(!(ax > ay * DRAG_RATIO && ax > DRAG_TRIGGER)){
      _DRAG.aborted = true; _DRAG = null;
      return;
    }
    _DRAG.applied = true;
    document.getElementById('grid').classList.add('dragging');
    _selApply(_DRAG.i0, _DRAG.add);
    updateSelBar();
    if(!_autoScrollRAF) _autoScrollRAF = requestAnimationFrame(_autoScrollStep);
  }

  const i = _phAt(ev.clientX, ev.clientY);
  if(i >= 0 && i !== _DRAG.lastI) _applyRange(_DRAG.i0, i, _DRAG.add);

  if(!_autoScrollRAF && _DRAG && _DRAG.applied){
    _autoScrollRAF = requestAnimationFrame(_autoScrollStep);
  }
}, {passive:true});

function _endDrag(){
  if(!_DRAG) return;
  if(_DRAG.applied) _DRAG_SKIP = Date.now();
  _DRAG = null;
  document.getElementById('grid').classList.remove('dragging');
  if(_autoScrollRAF){ cancelAnimationFrame(_autoScrollRAF); _autoScrollRAF = 0; }
}
document.addEventListener('pointerup', _endDrag);

document.addEventListener('pointercancel', () => {
  if(_autoScrollRAF){ cancelAnimationFrame(_autoScrollRAF); _autoScrollRAF = 0; }
});
document.addEventListener('touchend', _endDrag, {passive:true});
document.addEventListener('touchcancel', _endDrag, {passive:true});

(function(){
  const g = document.getElementById('grid');
  if(!g) return;
  g.addEventListener('touchmove', e => {
    if(_DRAG && _DRAG.applied) e.preventDefault();
  }, {passive:false});
})();

function syncSelClasses(){
  const nodes = document.querySelectorAll('#grid .ph');
  nodes.forEach((el, i) => {
    const p = ALL[i];
    if(p) el.classList.toggle('sel', SEL.has(p.rel));
  });
}

function updateSelBar(){
  $('#sel-n').textContent = `已选 ${SEL.size} 张`;

  $('#selbar').classList.toggle('show', SELMODE);

}

function selectAll(){
  const list = (typeof SHOWN !== 'undefined' && SHOWN && SHOWN.length) ? SHOWN : ALL;
  if(!list || !list.length) return;
  const allIn = list.every(p => SEL.has(p.rel));
  if(allIn) list.forEach(p => SEL.delete(p.rel));
  else      list.forEach(p => SEL.add(p.rel));
  const b = $('#btn-allsel');
  if(b) b.textContent = allIn ? '☑ 全选' : '☐ 全不选';
  syncSelClasses();          
  updateSelBar();
}

function clearSel(){

  exitSelMode();
}

async function tagSelected(){
  if(!SEL.size){ toast('先在图上点选要打标签的图（或点「全选」）'); return; }
  const t = prompt(`给选中的 ${SEL.size} 张加标签（多标签用逗号分隔；留空则移除全部标签）：`);
  if(t === null) return;
  const tags = t.split(/[,，]/).map(x=>x.trim()).filter(Boolean);
  try{
    const r = await post('/api/tags', {paths:[...SEL], add: tags, clear: tags.length === 0});
    if(r && r.error){ alert('打标签失败：' + r.error); return; }
    toast(tags.length ? `✅ 已加标签: ${tags.join(' / ')}（${SEL.size} 张）` : `✅ 已清空标签（${SEL.size} 张）`);
  }catch(e){
    alert('打标签失败：' + e);
    return;
  }
  const n = SEL.size;
  exitSelMode();
  const f = await api('/api/facets');
  renderTagChips(f.tags || []);
  load();
}

function _selRels(){
  if(!SEL.size){ toast('先点选图片'); return null; }
  return [...SEL];
}
function downloadSelected(){
  const rels = _selRels(); if(!rels) return;

  const url = '/api/dl/zip?' + rels.map(r => 'rel=' + encodeURIComponent(r)).join('&');
  toast(`打包 ${rels.length} 张中…`);
  const a = document.createElement('a');
  a.href = url; a.rel = 'noopener';
  document.body.appendChild(a); a.click(); a.remove();
}

async function favSelected(){
  if(!SEL.size){ toast('先点选图片'); return; }
  await post('/api/fav', {paths:[...SEL], value:true});
  toast(`已收藏 ${SEL.size} 张`);
  SEL.clear(); updateSelBar(); load();
}
async function unfavSelected(){
  if(!SEL.size){ toast('先点选图片'); return; }
  await post('/api/fav', {paths:[...SEL], value:false});
  toast(`已取消收藏 ${SEL.size} 张`);
  SEL.clear(); updateSelBar(); load();
}

async function quickRedrawSelected(){
  if(!SEL.size){ toast('先点选图片'); return; }
  const n = SEL.size;
  const mins = Math.ceil(n * secPerImage(8) / 60);   
  if(!confirm(`把选中的 ${n} 张各重抽一张？\n\n· 各自用原配置（提示词 / 尺寸 / 步数）\n· 只换随机种子\n· 串行跑，预计约 ${mins} 分钟\n· 结果放进「重抽_今天」相册\n\n现在开始？`)) return;
  toast(`已提交 ${n} 张，正在排队…`);
  const r = await post('/api/redraw', {rels: [...SEL], seed_mode: 'random'});
  if(r.error){ alert('无法重抽：' + r.error); return; }
  if(r.position > 0) toast(`⏳ 已排队（前面还有 ${r.position - 1} 个任务），轮到会自动开跑`);
  exitSelMode();
  load();
  pollRedraw(r.job);         

}

function pollGacha(jid){
  const tick = setInterval(async () => {
    let st;
    try { st = await api('/api/gacha/status?job=' + jid); } catch(e) { return; }
    if(!st || st.status === 'running') return;
    if(st.status === 'queued'){ setRedrawBadge(jid, st); return; }   
    clearInterval(tick);
    if(st.status === 'done'){
      toast(`✅ 出图 ${(st.files||[]).length} 张，已放入 ${st.outdir}`);
      _needReload = true;
      if(!$('#viewer').classList.contains('show')){ _needReload = false; load(); }
    } else {
      alert('ガチャ 失败：' + (st.error || (st.log || []).join('\n')));
    }
  }, 3000);
}

async function deleteSelected(){
  if(!SEL.size){ toast('先点选图片'); return; }
  const n = SEL.size;
  if(!confirm(`把选中的 ${n} 张移到废纸篓？\n\n（移到 macOS 废纸篓，不是永久删除，随时能从废纸篓恢复）`)) return;
  toast(`正在删除 ${n} 张…`);
  const r = await post('/api/delete', {paths:[...SEL]});
  const okN = (r.moved || 0), bad = (r.failed || []).length;
  toast(`🗑 已移到废纸篓 ${okN} 张` + (bad ? `（${bad} 张失败）` : ''));
  exitSelMode();
  load();
}

async function loadVersion(){
  try{
    const d = await api('/api/version');
    const el = document.getElementById('ver-badge');
    if(el && d && d.version) el.textContent = d.version;
  }catch(e){}
}

async function loadAlbums(){
  const d = await api('/api/albums');
  $('#album-cnt').textContent = '('+d.albums.length+')';
  $('#album-list').innerHTML = d.albums.map(a =>
    `<div class="album" onclick="jumpAlbum('${a.name}')">
       <div class="ico">📁</div>
       <div class="meta"><div class="nm">${a.name}</div>
         <div class="sub">${a.count} 张 · ${fmtSize(a.size)}</div></div>
       <div class="arr">›</div>
     </div>`).join('');
}

function fmtSize(b){ return b>1073741824 ? (b/1073741824).toFixed(2)+'G' : (b/1048576).toFixed(0)+'M'; }

function jumpAlbum(name){
  STATE.album = name; $('#f-album').value = name;
  switchTab('photos'); load();
}

function switchTab(t){

  $('#page-photos').style.display = t==='photos'?'block':'none';
  $('#page-albums').style.display = t==='albums'?'block':'none';
  window.scrollTo(0,0);
}

async function syncFavStatus(){
  const p = ALL[CUR]; if(!p) return;
  const reqRel = p.rel;
  try{
    const r = await api('/api/fav/get?rel=' + encodeURIComponent(reqRel));
    const cur = ALL[CUR];
    if(!cur || cur.rel !== reqRel) return;        
    if(r && typeof r.fav === 'boolean' && r.fav !== !!cur.fav){
      cur.fav = r.fav;
      renderViewer();                             
      syncThumbFav(cur.rel, r.fav);               
    }
  }catch(e){}
}
async function openViewer(i){
  CUR = i;

  const p0 = ALL[i];
  if(p0 && p0.rel){
    try{
      const r = await api('/api/fav/get?rel=' + encodeURIComponent(p0.rel));
      if(r && typeof r.fav === 'boolean') p0.fav = r.fav;
    }catch(e){}
  }
  CUR = i; renderViewer();
  saveView(ALL[i] ? ALL[i].rel : '');   
  $('#viewer').classList.add('show');
  $('#v-info').classList.remove('show');
  $('#btn-info').classList.remove('on');
  syncThumbFav(ALL[i] ? ALL[i].rel : '', !!(ALL[i] && ALL[i].fav));
  loadVersions(ALL[i] ? ALL[i].rel : '');         
}
function renderViewer(){
  const p = ALL[CUR]; if(!p) return;
  if(window._vzReset) window._vzReset();     
  $('#v-img').src = '/img?p='+encodeURIComponent(p.rel);
  $('#v-title').textContent = `${CUR+1}/${ALL.length}  ·  ${p.name}`;

  const _ot = (p.outfit||'').split(',').map(x=>x.trim()).filter(Boolean).map(cname).join('、');
  $('#v-info').textContent =
    `角色: ${short(p.char)}\n画风: ${styleCN(p.style)}   尺度: ${tierCN(p.tier)}${p.tier==='sex'&&posCN(p.action)?('  '+posCN(p.action)):''}\n` +
    `相册: ${p.dir}\nseed: ${p.seed}\n` +
    `服装: ${_ot||'（无记录）'}\n` +
    `标签: ${(p.tags||[]).join(' / ')||'无'}\n\n提示词:\n${p.prompt||'(无日志记录)'}`;
  $('#btn-info').classList.toggle('on', $('#v-info').classList.contains('show'));

  const ftxt = $('#btn-vfav-txt');
  if(ftxt) ftxt.textContent = p.fav ? '⭐ 已收藏' : '☆ 收藏';
  const fb = $('#btn-vfav');
  if(fb) fb.classList.toggle('on', !!p.fav);
  syncFavMark();          
  syncSaveOutfitBtn(p);
}

function syncSaveOutfitBtn(p){
  const b = $('#btn-vsave'); if(!b) return;
  const ok = !!(p && p.tier === 'fashion');
  b.disabled = !ok;
  b.classList.toggle('disabled', !ok);
  b.title = ok ? '快捷键 S　保存这张的服装搭配到搭配库'
               : ('保存搭配只在时尚档生效 —— 当前是' + tierCN(p && p.tier) + '档');
}

function syncThumbFav(rel, fav){
  const ph = document.querySelector('#grid .ph[data-rel="' + rel.replace(/"/g, '\\"') + '"]');
  if(!ph) return;
  const star = ph.querySelector('.favstar');
  if(fav && !star) ph.insertAdjacentHTML('beforeend', '<span class="favstar">⭐</span>');
  else if(!fav && star) star.remove();
}
async function loadVersions(rel){
  const box = $('#v-versions'); if(!box) return;
  const reqRel = rel;
  try{
    const d = await api('/api/versions?rel=' + encodeURIComponent(reqRel));
    const _cur = ALL[CUR];
    if(!_cur || (_cur.rel !== reqRel && _cur.name !== reqRel)) return;
    if(!d.items || d.items.length < 2){
      box.style.display = 'none'; box.innerHTML = ''; $('#v-vcount').textContent = '';
      return;
    }
    d.items.forEach(it => { if(!ALL.find(pp => pp.rel === it.rel)) ALL.push(it); });
    const cur = d.items.findIndex(it => it.rel === rel);
    box.innerHTML = d.items.map(it => {
      const chTip = (it.ch && it.n) ? `（第 ${it.ch}/${it.n} 章）` : '';
      const badge = (it.ch && it.n) ? `<span class="vch">第 ${it.ch}/${it.n} 章</span>` : '';
      return `<div class="vw"><img class="vthumb${it.rel === rel ? ' on' : ''}" data-rel="${it.rel}"
        data-ch="${it.ch || ''}" data-n="${it.n || ''}"
        src="/img?p=${encodeURIComponent(it.rel)}&t=thumb&v=${Math.round(it.mtime||0)}"
        title="${esc((it.name||'') + chTip)}">${badge}</div>`;
    }).join('');
    box.querySelectorAll('.vthumb').forEach(el => {
      el.onclick = () => jumpToVersion(el.dataset.rel);
      el.onerror = () => { (el.parentElement || el).remove(); updateVCount(rel); };
    });
    box.style.display = 'flex';
    updateVCount(rel);
  }catch(e){}
}
function updateVCount(rel){
  const arr = [...document.querySelectorAll('#v-versions .vthumb')];
  const box = $('#v-versions');
  if(!arr.length){ if(box) box.style.display = 'none'; $('#v-vcount').textContent = ''; return; }
  if(arr.length < 2){ if(box) box.style.display = 'none'; $('#v-vcount').textContent = ''; return; }
  const i = arr.findIndex(e => e.dataset.rel === rel);
  const curEl = arr[i < 0 ? 0 : i];
  const ch = curEl && curEl.dataset.ch, n = curEl && curEl.dataset.n;
  $('#v-vcount').textContent = (ch && n) ? `第 ${ch}/${n} 章` : `版本 ${(i < 0 ? 1 : i + 1)}/${arr.length}`;
}
function goHome(){
  ['char','chars','style','tier','album','tag','fav'].forEach(k => STATE[k] = '');
  STATE.sort = 'new';
  try{ CHAR_SEL.clear(); }catch(e){}
  try{ localStorage.setItem('xa_view',''); }catch(e){}
  $('#f-style').value = ''; $('#f-tier').value = ''; $('#f-album').value = ''; $('#f-work').value = '';
  $('#f-sort').value = 'new';
  $('#btn-fav').classList.remove('on');
  if(window.__facets) renderCharChips(window.__facets);
  load();
  window.scrollTo(0, 0);
}
function jumpToVersion(rel){
  const idx = ALL.findIndex(pp => pp.rel === rel || pp.name === rel);
  if(idx >= 0) openViewer(idx);
}
function cycleVersion(dir){
  const arr = [...document.querySelectorAll('#v-versions .vthumb')];
  if(arr.length < 2) return;
  let i = arr.findIndex(e => e.classList.contains('on')); if(i < 0) i = 0;
  arr[(i + dir + arr.length) % arr.length].click();
}
function navPhoto(d){
  if(CUR === null) return;
  const n = CUR + d;
  if(n < 0 || n >= ALL.length){
    if(n >= ALL.length && window.__hasMore) fetchPage(false).then(()=>{ CUR = Math.min(n, ALL.length-1); renderViewer(); syncFavStatus(); const _p2 = ALL[CUR]; if(_p2) loadVersions(_p2.rel); });
    return;
  }
  CUR = n; renderViewer();
  syncFavStatus();
  const _pp = ALL[CUR];
  if(_pp) loadVersions(_pp.rel);
}
function toggleInfo(){
  const on = !$('#v-info').classList.contains('show');
  $('#v-info').classList.toggle('show', on);
  $('#btn-info').classList.toggle('on', on);
}
function isFullView(){
  const v = document.getElementById('viewer');
  return !!document.fullscreenElement || !!(v && v.classList.contains('clean'));
}

function closeViewer(){
  try{ if(document.fullscreenElement) document.exitFullscreen(); }catch(e){}
  const _v = $('#viewer');
  if(_v && _v.classList.contains('clean')) _v.classList.remove('clean');
  $('#viewer').classList.remove('show');
  saveView('');
  const vb = $('#v-versions'); if(vb){ vb.style.display = 'none'; }
  const vc = $('#v-vcount'); if(vc) vc.textContent = '';
  if(_needReload){ _needReload = false; load(); }
}
function openRaw(){ const p = ALL[CUR]; if(p) window.open('/img?p='+encodeURIComponent(p.rel)+'&dl=1','_blank'); }

function toggleClean(){
  const v = $('#viewer'); if(!v) return;
  const on = v.classList.toggle('clean');
  const b = $('#btn-clean');
  if(b) b.textContent = on ? '👁 显示按钮' : '🧹 清屏';
  syncFavMark();
  if(on){
    try{
      if(!document.fullscreenElement && v.requestFullscreen) v.requestFullscreen();
    }catch(e){}
  }else{
    try{ if(document.fullscreenElement) document.exitFullscreen(); }catch(e){}
  }
  toast(on ? '⛶ 全屏浏览（快捷键照旧：F 收藏 · Q 快抽 · R 重抽 · T 标签 · Esc 退出）'
           : '👁 已退出全屏');
}

document.addEventListener('fullscreenchange', () => {
  if(document.fullscreenElement) return;
  const v = $('#viewer');
  if(v && v.classList.contains('clean')){
    v.classList.remove('clean');
    const b = $('#btn-clean'); if(b) b.textContent = '🧹 清屏';
    syncFavMark();
  }
});
function syncFavMark(){
  const p = ALL[CUR] || {};
  const m = $('#v-favmark');
  if(!m) return;
  m.textContent = p.fav ? '⭐' : '☆';
  m.classList.toggle('on', !!p.fav);
  m.title = p.fav ? '已收藏（F 键可取消）' : '未收藏（F 键收藏）';
}

document.addEventListener('keydown', e => {
  const t = e.target;
  if(t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
  if(document.querySelector('#repaint.show, #tagpicker.show, #rollpanel.show, #outfitpanel.show, #equippanel.show')) return;
  if(!$('#viewer').classList.contains('show')) return;
  const k = (e.key || '').toLowerCase();
  if(k === 'escape'){ closeViewer(); return; }
  if(k === 'arrowleft'){ navPhoto(-1); return; }
  if(k === 'arrowright'){ navPhoto(1); return; }
  if(k === 'arrowup' || k === 'arrowdown'){
    if(document.querySelectorAll('#v-versions .vthumb').length > 1){
      e.preventDefault();
      cycleVersion(k === 'arrowup' ? -1 : 1);
    }
    return;
  }
  if(k === 'f'){ e.preventDefault(); actFav(); return; }
  if(k === 'd'){ e.preventDefault(); actDelete(); return; }
  if(k === 'r'){ e.preventDefault(); actRedraw(); return; }
  if(k === 'q'){ e.preventDefault(); actQuickRedraw(); return; }
  if(k === 't'){ e.preventDefault(); actTag(); return; }
  if(k === 'c'){ e.preventDefault(); toggleClean(); return; }
  if(k === 'v'){ e.preventDefault(); cycleVersion(e.shiftKey ? -1 : 1); return; }
});

(function(){
  let x0=null, y0=null, moved=false, onButton=false;
  const body = document.getElementById('v-body');
  body.addEventListener('touchstart', e => {
    onButton = !!e.target.closest('button');
    x0=e.touches[0].clientX; y0=e.touches[0].clientY; moved=false;
    _vzPan = (VZ.s > 1.01 && !onButton)
      ? {x: e.touches[0].clientX - VZ.x, y: e.touches[0].clientY - VZ.y} : null;
  }, {passive:true});
  body.addEventListener('touchmove', e => {
    if(onButton || x0===null) return;
    const dx=e.touches[0].clientX-x0, dy=e.touches[0].clientY-y0;
    if(Math.abs(dx)>12 || Math.abs(dy)>12) moved = true;
    if(_vzPan && VZ.s > 1.01){
      VZ.x = e.touches[0].clientX - _vzPan.x;
      VZ.y = e.touches[0].clientY - _vzPan.y;
      _vzPaint(false);
      _vzClamp();
      _vzPaint(false);
    }
  }, {passive:true});
  body.addEventListener('touchend', e => {
    if(onButton){ onButton=false; x0=y0=null; moved=false; return; }
    if(x0===null) return;
    const dx = e.changedTouches[0].clientX - x0;
    const dy = e.changedTouches[0].clientY - y0;
    const tx = e.changedTouches[0].clientX, ty = e.changedTouches[0].clientY;
    if(!moved){
      const now = Date.now();
      if(now - _vzTap < 330 && Math.abs(tx-_vzTapX) < 45 && Math.abs(ty-_vzTapY) < 45){
        _vzTap = 0;
        _vzSkipClick = Date.now();
        _vzToggleAt(tx, ty);
        _vzPan = null; x0 = y0 = null; moved = false;
        return;
      }
      _vzTap = now; _vzTapX = tx; _vzTapY = ty;
    }
    if(VZ.s > 1.01){
      _vzPan = null;
      if(Math.abs(dx) > 12 || Math.abs(dy) > 12) _vzClamp(), _vzPaint();
      x0 = y0 = null; moved = false;
      return;
    }
    if(Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy)*1.5){
      navPhoto(dx < 0 ? 1 : -1);
    } else if(Math.abs(dy) > 70 && Math.abs(dy) > Math.abs(dx)){
      cycleVersion(dy > 0 ? 1 : -1);
    } else if(!moved){
      if(!isFullView() && e.target.tagName !== 'IMG') closeViewer();
    }
    x0 = y0 = null; moved = false;
  }, {passive:true});
})();

const VZ = {s: 1, x: 0, y: 0};
const VZ_SCALE = 2.6;
let _vzTap = 0, _vzTapX = 0, _vzTapY = 0, _vzPan = null, _vzSkipClick = 0;

function _vzPaint(anim){
  const im = document.getElementById('v-img'); if(!im) return;
  im.style.transformOrigin = '0 0';
  im.style.transition = anim === false ? 'none' : 'transform .22s cubic-bezier(.2,.7,.3,1)';
  im.style.transform = `translate(${VZ.x}px, ${VZ.y}px) scale(${VZ.s})`;
  im.style.cursor = VZ.s > 1.01 ? 'grab' : 'zoom-in';
  const vw = document.getElementById('viewer');
  if(vw) vw.classList.toggle('vzoomed', VZ.s > 1.01);
}

function _vzClamp(){
  const im = document.getElementById('v-img'); if(!im) return;
  if(VZ.s <= 1.001){ VZ.x = VZ.y = 0; return; }
  const r = im.getBoundingClientRect();
  const vw = window.innerWidth, vh = window.innerHeight;
  if(r.width <= vw) VZ.x += (vw - r.width) / 2 - r.left;
  else { if(r.left > 0) VZ.x -= r.left; else if(r.left + r.width < vw) VZ.x += vw - (r.left + r.width); }
  if(r.height <= vh) VZ.y += (vh - r.height) / 2 - r.top;
  else { if(r.top > 0) VZ.y -= r.top; else if(r.top + r.height < vh) VZ.y += vh - (r.top + r.height); }
}

function _vzReset(){
  VZ.s = 1; VZ.x = 0; VZ.y = 0; _vzPan = null;
  _vzPaint();
}
window._vzReset = _vzReset;

function _vzToggleAt(cx, cy){
  if(VZ.s > 1.01){ _vzReset(); return; }
  const im = document.getElementById('v-img'); if(!im) return;
  const r = im.getBoundingClientRect();
  const u = (cx - r.left) / Math.max(1, r.width);
  const v = (cy - r.top) / Math.max(1, r.height);
  VZ.x += (cx - u * r.width * VZ_SCALE) - r.left;
  VZ.y += (cy - v * r.height * VZ_SCALE) - r.top;
  VZ.s = VZ_SCALE;
  _vzClamp(); _vzPaint();
}

let _clickTimer = 0, _lastClickAt = 0;
document.getElementById('v-img').addEventListener('click', ev => {
  if(_vzSkipClick && Date.now() - _vzSkipClick < 400){
    clearTimeout(_clickTimer);
    return;
  }
  const now = Date.now();
  if(now - _lastClickAt < 330){
    _lastClickAt = 0;
    clearTimeout(_clickTimer);
    _vzSkipClick = now;
    _vzToggleAt(ev.clientX, ev.clientY);
    return;
  }
  _lastClickAt = now;
  if(VZ.s > 1.01) return;
  clearTimeout(_clickTimer);
  if(isFullView()) return;
  _clickTimer = setTimeout(() => closeViewer(), 260);
});
document.getElementById('v-img').addEventListener('pointerdown', ev => {
  if(VZ.s <= 1.01 || ev.pointerType === 'touch') return;
  ev.preventDefault();
  const sx = ev.clientX - VZ.x, sy = ev.clientY - VZ.y;
  const mv = e2 => {
    VZ.x = e2.clientX - sx; VZ.y = e2.clientY - sy;
    _vzPaint(false); _vzClamp(); _vzPaint(false);
  };
  const up = () => {
    document.removeEventListener('pointermove', mv);
    document.removeEventListener('pointerup', up);
    _vzPaint();
  };
  document.addEventListener('pointermove', mv);
  document.addEventListener('pointerup', up);
});

document.querySelectorAll('.floatbar button, .floatdel button, .nav').forEach(b => {
  b.addEventListener('touchstart', ev => ev.stopPropagation(), {passive:true});
});

let TAGLIB = {categories:[], cn:{}};
let TIERTAGS = {};
const TG_CN = {general:'通用', fashion:'时尚', tease:'擦边', exposed:'暴露', sex:'性爱'};
function tgClass(en){ const t = TIERTAGS[(en||'').trim().toLowerCase()] || TIERTAGS[en]; return t ? (' tg-' + t) : ''; }
function tgLabel(en){ const t = TIERTAGS[(en||'').trim().toLowerCase()] || TIERTAGS[en]; return t ? TG_CN[t] : ''; }
let RPCAT = {};
let CHAR_FEATS_MAP = {};
let RP_ORD = null;
let RP_TIER = '';
let WTIER = {};
let RP = {rel:'', tags:[]};
let PKCAT = '';
const RP_ORDER = ['quality','char','charfeat','eq_head','eq_face','eq_ears','eq_neck',
                  'eq_top','eq_hand','eq_chest','eq_bottom','eq_hip','eq_leg','eq_feet',
                  'outfit','eros_tease','eros_exposed','sexpos','sexroute','sexframing',
                  'penetration','ejac','eq_scene','eq_male','lower','action','pose','hand',
                  'leg','head','scene','camera','light','mood','pubic','style','misc','other'];
const RP_SIZES = [
  ['512x512','512²  方图'],['768x768','768²  方图'],['1024x1024','1024²  方图'],
  ['1280x1280','1280²  方图'],['1536x1536','1536²  方图（最大）'],
  ['512x768','竖  512×768'],['768x1152','竖  768×1152'],['1024x1536','竖  1024×1536'],
  ['768x512','横  768×512'],['1152x768','横  1152×768'],['1536x1024','横  1536×1024']
];

const RP_PRI = ['sexpos', 'penetration', 'sexframing', 'ejac', 'sexroute',
                'eq_scene', 'eq_male', 'eq_hip', 'eq_chest', 'eq_face', 'eq_top',
                'eq_bottom', 'eq_leg', 'eq_feet', 'eq_head', 'eq_ears', 'eq_neck', 'eq_hand',
                'eros_exposed', 'eros_tease', 'eros_fashion'];

async function ensureTaglib(){
  if(TAGLIB.categories.length) return;
  TAGLIB = await api('/api/taglib');
  TIERTAGS = TAGLIB.tiers || {};
  RPCAT = {};
  RP_ORD = (TAGLIB.order && TAGLIB.order.length) ? TAGLIB.order.slice() : null;
  WTIER = TAGLIB.cat_by_tier || {};
  CHAR_FEATS_MAP = TAGLIB.char_feats || {};
  Object.values(CHAR_FEATS_MAP).forEach(fs => fs.forEach(f => { if(!RPCAT[f]) RPCAT[f] = 'char_name'; }));
  const _co = TAGLIB.cat_of || {};
  Object.keys(_co).forEach(en => {
    RPCAT[en] = _co[en];
    en.split(',').forEach(t => { t = t.trim(); if(t && !RPCAT[t]) RPCAT[t] = _co[en]; });
  });
  if(!Object.keys(_co).length){
    const _pri = c => { const i = RP_PRI.indexOf(c.key); return i < 0 ? 999 : i; };
    [...TAGLIB.categories].sort((a, b) => _pri(a) - _pri(b)).forEach(c => (c.items || []).forEach(i => {
      RPCAT[i.en] = c.key;
      i.en.split(',').forEach(t => { t = t.trim(); if(t && !RPCAT[t]) RPCAT[t] = c.key; });
    }));
  }
  const KWR = [
    [/penis|pussy|anal|cum|creampie|fellatio|paizuri|footjob|handjob|cunnilingus|inserted|penetrat|nipple|clitoris|sperm/i, 'sexpos'],
    [/skirt|dress|shirt|hoodie|sweater|jeans|shorts|panties|lingerie|bikini|socks|thighhigh|boots|shoes|sleeve|neckline|outfit/i, 'outfit'],
    [/facing |from behind|profile view|three-quarter|from above|close-up|full body|upper body|wide angle|camera|pov/i, 'camera'],
    [/light|glow|shadow|backlit|candle|neon|sunset|moonlight/i, 'light'],
    [/standing|sitting|lying|kneeling|leaning|straddling|on all fours|reclining/i, 'pose'],
  ];
  RP.tags.forEach(t => {
    if(RPCAT[t]) return;
    for(const [re, k] of KWR){ if(re.test(t)){ RPCAT[t] = k; break; } }
  });
  const _kb = Object.keys(RPCAT).filter(k => k.length > 3).sort((a, b) => b.length - a.length);
  RP.tags.forEach(t => {
    if(RPCAT[t]) return;
    const tl = t.toLowerCase();
    for(const k of _kb){
      if(tl.includes(k)){
        RPCAT[t] = RPCAT[k];
        if(WTIER[k]) WTIER[t] = WTIER[k];
        break;
      }
    }
  });
}
function cname(t){ return (TAGLIB.cn && TAGLIB.cn[t]) || composeCN(t) || t; }

async function saveOutfit(){
  const p = ALL[CUR]; if(!p) return;
  if(p.tier !== 'fashion'){ toast('保存搭配只在时尚档生效（这张是 ' + (p.tier||'?') + '）'); return; }
  const r = await post('/api/outfit/save', {rel: p.rel});
  if(r.error){ alert('保存失败：' + r.error); return; }
  toast('👗 已存进搭配库（' + (r.prompt_seg||'').slice(0,30) + '…）');
}
async function openOutfitPanel(){
  const p = ALL[CUR]; if(!p) return;
  if(p.tier !== 'fashion'){ toast('换装只在时尚档生效（这张是 ' + (p.tier||'?') + '）'); return; }
  const d = await post('/api/outfit/list', {});
  const sets = d.sets || [], outs = d.outfits || [];
  $('#op-sets').innerHTML = sets.map(s =>
    `<button onclick="applySet('${s.key}')">${s.label}</button>`).join('') || '<i>（无）</i>';
  $('#op-thumbs').innerHTML = outs.length ? outs.map(o => {
    const tip = Object.entries(o.parts||{}).map(([k,v]) => `${k}: ${v}`).join('\n');
    return `<div class="op-card" onclick="applyOutfit('${o.id}')">
      <img src="/img?p=${encodeURIComponent(o.thumb)}" loading="lazy">
      <div class="op-name">${(o.name||'').slice(0,16)}</div>
      <div class="op-tip">${(o.prompt_seg||'').replace(/</g,'&lt;')}</div></div>`;
  }).join('') : '<i>还没有保存过搭配 —— 在大图页按 S 存一套</i>';
  $('#outfitpanel').classList.add('show');
}
function closeOutfitPanel(){ $('#outfitpanel').classList.remove('show'); }
async function applyOutfit(id){
  const p = ALL[CUR]; if(!p) return;
  closeRepaint(); closeOutfitPanel();
  toast('👗 换成这套搭配…');
  const r = await post('/api/redraw', {rel: p.rel, quick: 'outfit', outfit_id: id});
  if(r.error){ alert('换装失败：' + r.error); return; }
  pollRedraw(r.job);
}
async function applySet(key){
  const p = ALL[CUR]; if(!p) return;
  closeRepaint(); closeOutfitPanel();
  toast('👗 按套装「' + key + '」随机组合…');
  const r = await post('/api/redraw', {rel: p.rel, quick: 'set', set_key: key});
  if(r.error){ alert('换装失败：' + r.error); return; }
  pollRedraw(r.job);
}

function bindDbl(el, fn){
  let last = 0;
  el.addEventListener('click', (e) => {
    const now = Date.now();
    if(now - last < 320){ last = 0; e.preventDefault(); e.stopPropagation(); fn(); }
    else last = now;
  });
}

async function openRepaint(mode){
  const p = ALL[CUR]; if(!p) return;
  await ensureTaglib();
  RP.rel = p.rel;
  RP_TIER = (p.tier || '').toLowerCase();
  RP.tags = (p.prompt || '').split(',').map(s => s.trim()).filter(Boolean);
  const srcSize = p.size || '';
  let opts = RP_SIZES.map(([v, t]) => `<option value="${v}">${t}</option>`);
  if(srcSize && !RP_SIZES.some(([v]) => v === srcSize))
    opts.unshift(`<option value="${srcSize}">原图  ${srcSize}</option>`);
  $('#rp-size').innerHTML = opts.join('');
  $('#rp-size').value = srcSize || '1024x1536';
  $('#rp-steps').innerHTML = Array.from({length:9}, (_, i) => i + 4)
      .map(n => `<option value="${n}">${n} 步</option>`).join('');
  $('#rp-steps').value = String(p.steps || 8);
  $('#rp-count').innerHTML = [1,2,3,4].map(n => `<option value="${n}">${n} 张</option>`).join('');

  $('#rp-seed').value = 'inherit';
  $('#rp-src').textContent = p.name;
  ['#rp-size','#rp-steps','#rp-count','#rp-seed'].forEach(id => { $(id).onchange = updateRPHint; });
  updateRPHint();
  renderRPTags();
  $('#repaint').classList.add('show');
}
function closeRepaint(){ $('#repaint').classList.remove('show'); }

function secPerImage(st){ return Math.round((+st || 8) * 12 + 20); }   

function updateRPHint(){
  const n = $('#rp-count').value, sm = $('#rp-seed').value, st = $('#rp-steps').value;
  const sz = $('#rp-size').value;
  const secPer = secPerImage(st);                 
  $('#rp-hint').textContent =
    `共 ${n} 张 · ${sz} · ${st} 步 · ${sm === 'inherit' ? '继承原图种子' : '随机种子'}` +
    `　预计 ${(n * secPer / 60).toFixed(1)} 分钟（约 ${secPer} 秒/张）` +
    (sm === 'inherit' ? '　⚠️ 继承种子只会跑 1 张' : '') +
    '　提示词未改动 = 原样重抽';
  if(sm === 'inherit') $('#rp-count').value = '1';
}

function rpGrouped(){
  const g = {};

  const subOf = t => (WTIER[t] && RP_TIER && WTIER[t][RP_TIER]) || RPCAT[t] || 'zz_other';
  RP.tags.forEach(t => { const k = subOf(t); (g[k] = g[k] || []).push(t); });
  const ORD = RP_ORD || RP_ORDER;
  const keys = ORD.filter(k => g[k]).concat(Object.keys(g).filter(k => !ORD.includes(k)));
  return keys.map(k => [k, g[k]]);
}
function rpPrompt(){
  return rpGrouped().map(([k, arr]) => arr.join(', ')).join(', ');
}

function featCovered(){
  const own = new Set();
  RP.tags.forEach(t => (CHAR_FEATS_MAP[t] || []).forEach(f => own.add(f)));
  return own;
}
function renderRPTags(){
  const _cover = featCovered();
  const groups = rpGrouped()
    .map(([k, arr]) => [k, arr.filter(t => !_cover.has(t))])
    .filter(([k, arr]) => arr.length);
  if(!groups.length){
    $('#rp-tags').innerHTML = '<div class="rp-grp"><h4>（空）</h4></div>';
    return;
  }
  $('#rp-tags').innerHTML = groups.map(([k, arr]) => {
    const label = (TAGLIB.cat_labels || {})[k]
                  || ((TAGLIB.categories || []).find(c => c.key === k) || {}).label
                  || '其他';

    const tier = ((TAGLIB.cat_tiers || {})[k]) || 'general';
    const tcls = tier && tier !== 'general' ? (' tg-' + tier) : '';
    const chips = arr.map(t => {
      const i = RP.tags.indexOf(t);
      return `<span class="tg${tcls}" data-i="${i}" title="${t}">${cname(t)}</span>`;
    }).join('');
    const dot = `<i class="cdot c-${tier}"></i>`;
    return `<div class="rp-grp"><h4>${dot}${label} · ${arr.length}</h4><div class="rp-tags">${chips}</div></div>`;
  }).join('');
  document.querySelectorAll('#rp-tags .tg').forEach(el => {
    bindDbl(el, () => {
      const t = RP.tags[+el.dataset.i];
      if(t && CHAR_FEATS_MAP[t] && RP.tags.includes(t)){ toggleTag(t); renderRPTags(); return; }
      RP.tags.splice(+el.dataset.i, 1); renderRPTags();
    });
  });
}

let QP_ITEMS = [];
let QP_TIMER = null;
let QP_DIRTY = false;      
let QP_BASE = [];          

async function openQueuePanel(){
  $('#queuepanel').classList.add('show');
  QP_DIRTY = false;
  await refreshQueuePanel();
  clearInterval(QP_TIMER);
  QP_TIMER = setInterval(refreshQueuePanel, 4000);   
}
function closeQueuePanel(){
  $('#queuepanel').classList.remove('show');
  clearInterval(QP_TIMER); QP_TIMER = null;
}
async function refreshQueuePanel(){
  if(QP_DIRTY) return;            
  try{
    const r = await api('/api/redraw_active');
    QP_ITEMS = r.queue || [];
    renderQueuePanel(r);
  }catch(e){}
}
function renderQueuePanel(r){
  r = r || {};
  const cur = r.current;
  const list = $('#qp-list');

  const nq = r.queued || 0, nd = r.done || 0, nf = r.failed || 0;
  const nr = QP_ITEMS.filter(x => ['running','starting'].includes(x.status || '')).length
             || (r.running ? 1 : 0);
  const parts = [];
  if(nr) parts.push(`跑 ${nr}`);
  if(nq) parts.push(`等待 ${nq}`);
  if(nd) parts.push(`完成 ${nd}`);
  if(nf) parts.push(`失败 ${nf}`);
  $('#qp-n').textContent = parts.length ? `（${parts.join(' · ')}）` : '';

  const ST = {queued: ['⏳', '等'], running: ['▶️', '跑'], starting: ['▶️', '跑'],
              done: ['✅', '完成'], failed: ['❌', '失败'], cancelled: ['🚫', '已取消']};
  const doneOrFail = x => ['done', 'failed', 'cancelled'].includes(x.status || '');

  let html = '';
  if(cur && !QP_ITEMS.some(x => x.job === cur.job)){
    html += `<div class="qp-run"><div class="nm">▶️ 正在跑：${short(cur.char)}</div>`
          + `<div class="mt" style="font-size:11px;color:var(--fg2);margin-top:2px">`
          + `${cur.tier_cn || ''}${cur.count > 1 ? ` · ${cur.count} 张` : ''}</div></div>`;
  }
  if(!QP_ITEMS.length){
    html += `<div class="qp-empty">${cur ? '队列空了，跑完这个就收工' : '队列是空的<br>在图上点「重抽」就会排进来'}</div>`;
    list.innerHTML = html;
    $('#qp-bar').style.display = 'none';
    return;
  }
  html += QP_ITEMS.map((it, i) => {
    const st = ST[it.status] || ['•', it.status || ''];
    const df = doneOrFail(it);

    const rel = String(it.out || it.src || '').replace(/"/g, '&quot;');
    const clickable = (it.status === 'done' && rel);
    const hint = clickable ? ' · 点击看大图' : '';
    return `<div class="qp-item${df ? ' qp-' + it.status : ''}" data-job="${it.job}" data-i="${i}" data-st="${it.status || ''}">
       <span class="grip"${df ? ' style="opacity:.25"' : ''}>≡</span><span class="idx">${st[0]}</span>
       <div class="body"><div class="nm${clickable ? ' clickable' : ''}" data-rel="${rel}" data-st="${it.status || ''}"${clickable ? ' title="点这里跳到这张的大图页"' : ''}>${short(it.char)}<span class="st">${st[1]}</span></div>
         <div class="mt">${it.tier_cn || '?'}${it.count > 1 ? ` · ${it.count} 张` : ''}${hint}</div></div>
       <button class="del" onclick="cancelQueueItem('${it.job}')" title="${df ? '删除这条记录' : '移出队列'}">✕</button>
     </div>`;
  }).join('');
  list.innerHTML = html;
  $('#qp-bar').style.display = QP_DIRTY ? 'flex' : 'none';
  bindQueueClicks();
  bindQueueDrag();
}
function bindQueueClicks(){
  document.querySelectorAll('#qp-list .qp-item .nm').forEach(nm => {
    const st = nm.dataset.st || '';
    if(st === 'done'){
      const rel = nm.dataset.rel || '';
      nm.onclick = () => openByRel(rel);
    } else if(st === 'failed'){
      nm.onclick = () => toast('这条失败了，没有产物（可点下方「🔄 重跑失败」重试）');
    }
  });
}
function _relBase(s){
  return String(s || '').replace(/\\/g, '/').replace(/^\/+/, '')
           .replace(/^自动抽卡\//, '').split('/').pop().replace(/\.png$/i, '');
}
async function openByRel(rel){
  if(!rel){ toast('这条没有可跳转的图'); return; }
  const name = String(rel).split('/').pop();
  const base = _relBase(rel);
  const find = () => ALL.findIndex(p => p.rel === rel || p.name === rel || p.name === name
                                     || _relBase(p.rel) === base || _relBase(p.name) === base);
  let idx = find();
  if(idx < 0){
    for(let i = 0; i < 20 && window.__hasMore; i++){
      await fetchPage(false);
      idx = find();
      if(idx >= 0) break;
    }
  }
  if(idx < 0){
    try{
      if(typeof STATE !== 'undefined' && STATE.album){ STATE.album = ''; }
      await load();
      idx = find();
    }catch(e){}
  }
  if(idx < 0){ toast('找不到这张图（可能已被删除，或不在当前筛选里）'); return; }
  closeQueuePanel();
  openViewer(idx);
}
async function cancelQueueItem(jid){
  if(!confirm('把这个任务移出队列？')) return;
  const r = await post('/api/redraw/cancel', {job: jid});
  QP_DIRTY = false;
  QP_ITEMS = r.queue || [];
  renderQueuePanel(r);
}
async function clearDone(){
  const n = QP_ITEMS.filter(x => x.status === 'done').length;
  if(!n){ toast('没有已完成的任务'); return; }
  if(!confirm(`清掉 ${n} 个已完成的任务？\n（失败的不动，那是留着重跑的）`)) return;
  try{
    const r = await post('/api/redraw/clear-done', {});
    QP_ITEMS = r.queue || []; QP_DIRTY = false;
    renderQueuePanel(r);
    toast(`🧹 清掉 ${n} 个已完成`);
  }catch(e){ toast('❌ 清除失败'); }
}
async function retryFailed(){
  const n = QP_ITEMS.filter(x => x.status === 'failed').length;
  if(!n){ toast('没有失败的任务'); return; }
  try{
    const r = await post('/api/redraw/retry-failed', {});
    QP_ITEMS = r.queue || []; QP_DIRTY = false;
    renderQueuePanel(r);
    toast(`🔄 ${r.retried || n} 个失败任务重新排队`);
  }catch(e){ toast('❌ 重跑失败'); }
}
async function saveQueueOrder(){
  try{
    const r = await post('/api/redraw/reorder', {order: QP_ITEMS.map(x => x.job)});
    QP_ITEMS = r.queue || QP_ITEMS;
    QP_DIRTY = false;
    renderQueuePanel(r);
    toast('✅ 队列顺序已保存');
  }catch(e){ toast('❌ 保存失败'); }
}
function resetQueueOrder(){
  if(!QP_BASE.length){ QP_DIRTY = false; refreshQueuePanel(); return; }
  const map = {}; QP_ITEMS.forEach(x => map[x.job] = x);
  QP_ITEMS = QP_BASE.map(j => map[j]).filter(Boolean);
  QP_DIRTY = false;
  refreshQueuePanel();
  toast('已还原顺序');
}
function bindQueueDrag(){
  const list = $('#qp-list');
  let dragEl = null, startY = 0, curIdx = -1;

  const startDrag = (el, ev) => {
    if(!QP_DIRTY) QP_BASE = QP_ITEMS.map(x => x.job);
    dragEl = el; curIdx = +el.dataset.i; startY = ev.clientY;
    el.classList.add('dragging');
    try{ el.setPointerCapture(ev.pointerId); }catch(e){}
    if(ev.cancelable) ev.preventDefault();
  };

  list.querySelectorAll('.qp-item').forEach(el => {
    if(['done','failed','cancelled'].includes(el.dataset.st || '')) return;

    const grip = el.querySelector('.grip');
    if(grip){
      grip.addEventListener('pointerdown', ev => {
        ev.stopPropagation();
        startDrag(el, ev);
      });
    }

    el.addEventListener('pointermove', ev => {
      if(dragEl !== el) return;
      const rowH = el.offsetHeight + 8;
      const target = Math.max(0, Math.min(QP_ITEMS.length - 1,
                     curIdx + Math.round((ev.clientY - startY) / rowH)));
      if(target !== +el.dataset.i){
        const from = +el.dataset.i;
        const [moved] = QP_ITEMS.splice(from, 1);
        QP_ITEMS.splice(target, 0, moved);
        const nodes = [...list.querySelectorAll('.qp-item')];
        list.innerHTML = '';
        QP_ITEMS.forEach((it, i) => {
          const n = nodes.find(x => x.dataset.job === it.job);
          if(n){ n.dataset.i = i; n.querySelector('.idx').textContent = i + 1; list.appendChild(n); }
        });
        startY = ev.clientY; curIdx = target;
      }
    });
    const end = () => {
      if(dragEl !== el) return;
      el.classList.remove('dragging');
      dragEl = null;
      QP_DIRTY = true;
      $('#qp-save').textContent = `确认排序（${QP_ITEMS.length} 项）`;
      $('#qp-bar').style.display = 'flex';
    };
    el.addEventListener('pointerup', end);
    el.addEventListener('pointercancel', end);
  });
}

async function openRollPanel(){
  $('#rollpanel').classList.add('show');
  await refreshRoll();
  rollPrioLoad();
}
function closeRollPanel(){ $('#rollpanel').classList.remove('show'); }

/* ═══ ⭐ 2026-10-06：抽卡机优先级开关 ═══
   晚上 ⚡ 高性能（每张快 ~16s，但抢 CPU）；白天 🌙 让路（跟手，慢 16s/张）。
   真身是 launchd plist 里的 Nice/ProcessType —— 切换会重启抽卡机（当前这张会中断） */
async function rollPrioLoad(){
  try{ rollPrioPaint(await post('/api/roll/prio', {})); }catch(e){}
}
function rollPrioPaint(d){
  if(!d || !d.mode || d.mode === '?') return;
  const hi = d.mode === 'high';
  const H = $('#prio-high'), L = $('#prio-low');
  if(H){ H.style.outline = hi ? '2px solid #ff2e63' : 'none'; H.style.opacity = hi ? 1 : .55; }
  if(L){ L.style.outline = hi ? 'none' : '2px solid #ff2e63'; L.style.opacity = hi ? .55 : 1; }
  const now = $('#prio-now'); if(now) now.textContent = '当前：' + (hi ? '⚡ 高性能' : '🌙 让路');
  const hint = $('#prio-hint');
  if(hint) hint.textContent = hi
    ? '每张快约 16 秒；出图时会抢 CPU，同时用电脑可能没那么跟手。'
    : '被系统降级调度，出图慢约 16 秒/张；同时用电脑更跟手。';
}
async function rollPrio(mode){
  const hi = mode === 'high';
  if(!confirm(hi ? '切到 ⚡ 高性能？会重启抽卡机（当前正在画的那张会中断重来）'
                 : '切到 🌙 让路？会重启抽卡机（当前正在画的那张会中断重来）')) return;
  const r = await post('/api/roll/prio', {mode});
  if(!r || !r.ok){ alert('切换失败：' + ((r && r.detail) || '未知错误')); return; }
  rollPrioPaint(r);
  toast(hi ? '⚡ 已切高性能' : '🌙 已切让路');
  setTimeout(refreshRoll, 1200);
}

/* ═══ 状态灯 ═══
   · 真相源 = 后端 /api/roll/status 的 running（抽卡机进程在不在） */
function machineState(d){
  d = d || {};
  return { run: !!d.running };
}
function paintLamp(id, txtId, on, onTxt, offTxt){
  const el = document.getElementById(id); if(el) el.classList.toggle('on', on);
  const t = document.getElementById(txtId); if(t) t.textContent = on ? onTxt : offTxt;
}
async function openEquipPanel(){
  $('#equippanel').classList.add('show');
  await refreshEquip();
}
function closeEquipPanel(){ $('#equippanel').classList.remove('show'); }
async function refreshEquip(){
  loadPools();
  try{
    const d = await api('/api/roll/status');
    const rp = await rollParamsLoad(true);
    const rpP = (rp && rp.params) || {};
    const tw = rpP.tier_weights || (d.config && d.config.tier_weights) || {};
    ['fashion','tease','exposed','sex'].forEach(k => {
      const el = $('#tw-' + k); if(el) el.value = (tw[k] !== undefined ? tw[k] : 0);
    });
    const eh = $('#equip-params-hint');
    if(eh && rp && rp.params) eh.textContent =
      `参数模块：每日上限 ${rpP.daily_cap} 张 · 尺寸 ${rpP.size_mode || ''}`;
    applyEquipLamp(d);
    window.scrollTo(0,0);
  }catch(e){ toast('读取失败：' + e.message); }
}
function applyEquipLamp(d){
  const { run } = machineState(d);
  paintLamp('equip-lamp', 'equip-lamp-txt', run, '🟢 正在出卡', '⚪ 未出卡');
  $('#equip-state').textContent = run ? '出卡中' : '已停止';
}

/* ═══ 候选池总览═══
   设置菜单里直接看池子里有什么 —— 中文显示、按新拆的池子分类。
   数据来自 /api/pools（后端扫 pools/ 包），所以看到的就是抽卡机真在用的那份。 */
let POOLS = null;
function esc(s){ return String(s == null ? '' : s).replace(/[&<>"']/g,
  c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

/* ═══════════════════════════════════════════════════════════
   ⭐ 装备机：分类底纹边框 / 尺度配色 /
      旧标签归「其他」默认禁用不可点 / 缺翻译标记 / 角色单击展开特征 / 统一双击禁用
   ──────────────────────────────────────────────────────────
   · 配色（约定）：时尚挂=蓝 · 通用词=白 · 擦边=粉 · 暴露=橙 · 性爱=红
   · 旧标签 = 历史上停用/残留的那批词（见下面 LEGACY_TAGS 快照）→ 统一归「其他」。
   · 角色特征数据 = CHAR_TAGS 快照（改了 pools/characters.py 之后要重新生成）。
   ═══════════════════════════════════════════════════════════ */

const LEGACY_TAGS = new Set([
  'hips pressed together','girl','hips against her','ass','riding','lifted against the wall',
  'oral','giving head','tongue licking the tip','tongue licking the shaft from below',
  'tongue teasing the tip','penis resting on her face','tongue running up the length',
  'breasts squeezing it','breasts pressed together around it',
  'tongue licking the tip between her breasts','nipples brushing the shaft',
  'both soles rubbing it','toes teasing the tip','being licked','his tongue on her pussy',
  'tongue between her folds','licking her clit','mouth between her legs','his tongue inside her',
  'bedroom eyes','half-closed eyes','panting softly','lips parted','blissful smile',
  'lost in pleasure','embarrassed expression','glistening eyes','mouth slightly open','trembling',
  'first person view','close-up on the connection point','pussy and penis visible',
  'dress pulled up','other',
]);

const CHAR_TAGS = {"hatsune_miku":[{"en":"aqua hair","cn":"水蓝发","cat":"hair","lock":true},{"en":"very long twintails","cn":"超长双马尾","cat":"hair","lock":true},{"en":"aqua eyes","cn":"水蓝眼","cat":"eyes","lock":true}]};
const CHAR_FEAT_ORDER = ['hair','eyes','body','face','extra','default_outfit','props'];
const CHAR_FEAT_LABEL = {hair:'头发', eyes:'眼睛', body:'身材', face:'面部',
  extra:'附加特征', default_outfit:'👗 原皮', props:'道具'};

const _EQ_SEX = new Set(['SEX_FACE','SEX_FACE_BY_ATT','SEX_FACE_WATCH','SEX_SCENES',
  'SEX_PARTNER','TOYS','FEATURE_RULES','MALE_TAG','MALE_FEET']);
const _EQ_EXPOSED = new Set(['CHEST_EXPOSE','REAR_EXPOSE']);
const _EQ_FASHION = new Set(['TOPS','BOTTOMS','SHOES','LEGWEAR','HEADWEAR','NECKWEAR',
  'EARRINGS','EYEWEAR','SLEEVES','DECO_CAP','UNDERWEAR','SET_SLOTS','CHAR_PROPS','GENERIC_PROPS']);
function poolTier(gkey){
  const gkey_s = String(gkey || '');
  const i = gkey_s.indexOf('.');
  const g = i < 0 ? gkey_s : gkey_s.slice(0, i);
  const p = i < 0 ? '' : gkey_s.slice(i + 1);
  if(g === 'fashion' || g === 'composition') return 'fashion';
  if(g === 'eros') return p === 'EROS_FASHION' ? 'fashion'
                       : p === 'EROS_TEASE_UNITS' ? 'tease'
                       : p === 'EROS_EXPOSED_UNITS' ? 'exposed' : 'normal';
  if(g === 'sex_router') return 'sex';
  if(g === 'equip_machine') return _EQ_SEX.has(p) ? 'sex'
                               : _EQ_EXPOSED.has(p) ? 'exposed'
                               : _EQ_FASHION.has(p) ? 'fashion' : 'normal';
  return 'normal';
}

let POOL_OFF_SET = new Set();
const FEATOFF_LS = 'featoff_fold';
function featOffLS(){
  try{ return new Set(JSON.parse(localStorage.getItem(FEATOFF_LS) || '[]')); }catch(e){ return new Set(); }
}
function featOffSet(en, on){
  const s = featOffLS(); on ? s.add(en) : s.delete(en);
  try{ localStorage.setItem(FEATOFF_LS, JSON.stringify([...s])); }catch(e){}
}

function piSpan(it, gkey, isChar){
  const leg = LEGACY_TAGS.has(it.en);
  const off = leg || !!it.off;
  const tier = leg ? 'legacy' : poolTier(gkey);
  const noCn = (!it.cn && !it.key);
  const tip = leg
    ? `旧标签 / 已停用\n${it.en}\n（历史残留，已下线，不可启用）`
    : [it.en].concat(it.extra || []).join('\n') + (noCn ? '\n⚠ 缺中文翻译' : '');
  const cls = 'pi t-' + tier + (off ? ' off' : '') + (it.extra ? ' has-ex' : '')
            + (noCn ? ' no-cn' : '') + (leg ? ' legacy' : '') + (isChar ? ' char' : '');
  return `<span class="${cls}" data-g="${esc(gkey)}" data-en="${esc(it.en)}"`
       + ` title="${esc(tip)}">${esc(it.cn || it.en)}</span>`;
}

function featSpan(f){
  const locked = !!f.lock;
  const noCn = !f.cn;
  const off = !locked && POOL_OFF_SET.has(f.en);
  const tier = f.cat === 'default_outfit' ? 'fashion' : 'normal';
  const tip = (locked ? '🔒 本体特征，删了也会出\n' : '双击禁用 / 启用该特征\n')
            + f.en + (noCn ? '\n⚠ 缺中文翻译' : '');
  const cls = 'pi' + (locked ? ' feat-locked' : ' t-' + tier) + (off ? ' off' : '')
            + (noCn ? ' no-cn' : '');
  return `<span class="${cls}" data-g="characters.FEATURES" data-en="${esc(f.en)}"`
       + ` title="${esc(tip)}">${esc(f.cn || f.en)}</span>`;
}

function toggleCharExpand(el){
  const box = $('#char-expand'); if(!box) return;
  const tag = el.dataset.en;
  if(!box.hidden && box.dataset.for === tag){ box.hidden = true; box.dataset.for = ''; return; }
  box.hidden = false; box.dataset.for = tag;
  const feats = CHAR_TAGS[tag];
  if(!feats){
    box.innerHTML = `<div class="feat-head">${esc(tag)}</div>` +
      '<p class="rp-hint">这个角色没有特征展开数据。</p>';
    return;
  }
  const cats = {};
  feats.forEach(f => (cats[f.cat] = cats[f.cat] || []).push(f));
  const order = CHAR_FEAT_ORDER.concat(Object.keys(cats).filter(k => CHAR_FEAT_ORDER.indexOf(k) < 0));
  const body = order.filter(k => cats[k]).map(k =>
    `<div class="feat-cat feat-cat-${esc(k)}${k === 'default_outfit' ? ' feat-cat-outfit' : ''}">`
    + `<span class="feat-cat-n">${CHAR_FEAT_LABEL[k] || k} · ${cats[k].length}</span>`
    + `<div class="pool-items">${cats[k].map(featSpan).join('')}</div></div>`).join('');
  box.innerHTML = `<div class="feat-head">${esc(tag)} 的特征`
    + `　<span class="feat-sub">双击可单独禁用 · 🔒 灰色 = 本体特征（删了也会出）</span></div>` + body;
  box.querySelectorAll('.pi').forEach(chip => {
    if(chip.classList.contains('feat-locked')) return;
    bindDbl(chip, () => togglePi(chip));
  });
  box.scrollIntoView({block:'nearest', behavior:'smooth'});
}

async function loadPools(force){
  if (POOLS && !force) return;
  const box = $('#pools-box');
  box.innerHTML = '<p class="rp-hint">加载中…</p>';
  try{
    POOLS = await api('/api/pools');
  }catch(e){
    box.innerHTML = '<p class="rp-hint">读取失败：' + esc(e.message) + '</p>';
    return;
  }
  renderPools();
}

function renderPools(){
  const box = $('#pools-box');
  const groups = (POOLS && POOLS.groups) || [];
  let tot = 0;
  const legacy = [];

  const groupHtml = groups.map(g => {
    let n = 0;
    const ps = g.pools.map(p => {
      const items = p.items.filter(it => {
        if(LEGACY_TAGS.has(it.en)){ legacy.push({it, gkey: p.gkey}); return false; }
        return true;
      });
      if(p.gkey === 'characters.DEFAULT_OUTFIT'){
        p.items.forEach(it => { if(it.off && !it.key) featOffSet(it.en, true); });
        return '';
      }
      if(!items.length) return '';
      n += items.length;
      const isChar = (p.gkey === 'characters.CHARACTERS');
      const chips = items.map(it => piSpan(it, p.gkey, isChar)).join('');
      const expand = '';
      return `<details class="pool-p"><summary><span>${esc(p.name)}</span><em>${items.length}</em></summary>`
           + `<div class="pool-items">${chips}</div>${expand}</details>`;
    }).filter(Boolean).join('');
    if(!ps) return '';
    tot += n;
    return `<details class="pool-g"><summary><span>${g.icon || ''} ${esc(g.label)}</span><em>${n}</em></summary>${ps}</details>`;
  }).filter(Boolean).join('');

  let extra = '';
  if(legacy.length){
    const chips = legacy.map(({it, gkey}) => piSpan(it, gkey, false)).join('');
    extra = `<details class="pool-g legacy-g"><summary><span>🗑 其他</span><em>${legacy.length}</em></summary>`
          + `<details class="pool-p" open><summary><span>旧标签（已停用）</span><em>${legacy.length}</em></summary>`
          + `<div class="pool-items">${chips}</div>`
          + `<p class="rp-hint">这些是历史残留的旧标签（不在 pools/ 里）：已下线 · 默认禁用 · 不可启用。</p>`
          + `</details></details>`;
  }

  box.innerHTML = (groupHtml + extra) || '<p class="rp-hint">（空）</p>';
  $('#pools-n').textContent = `${tot + legacy.length} 条 / ${groups.length} 组`
                            + (legacy.length ? ` + 其他 ${legacy.length}` : '');

  POOL_OFF_SET = new Set();
  box.querySelectorAll('.pi.off').forEach(el => POOL_OFF_SET.add(el.dataset.en));
  featOffLS().forEach(en => POOL_OFF_SET.add(en));

  box.querySelectorAll('.pi').forEach(el => {
    if(el.classList.contains('legacy')) return;
    if(el.classList.contains('char')) return;
    bindDbl(el, () => togglePi(el));
  });
  box.querySelectorAll('.pi.char').forEach(el => {
    let last = 0;
    el.addEventListener('click', e => {
      const now = Date.now();
      if(now - last < 320){ last = 0; e.preventDefault(); e.stopPropagation(); togglePi(el); return; }
      last = now;
      setTimeout(() => { if(last !== now) return; toggleCharExpand(el); }, 300);
    });
  });
}

function filterPools(){
  const q = ($('#pools-q').value || '').trim().toLowerCase();
  document.querySelectorAll('#pools-box .pool-p').forEach(d => {
    let hit = 0;
    d.querySelectorAll('.pi').forEach(el => {
      const ok = !q || el.textContent.toLowerCase().includes(q)
                  || (el.title || '').toLowerCase().includes(q);
      el.classList.toggle('hide', !ok);
      if(ok) hit++;
    });
    d.classList.toggle('hide', q && !hit);
    if(q) d.open = !!hit;
  });
  document.querySelectorAll('#pools-box .pool-g').forEach(d => {
    const any = [...d.querySelectorAll('.pool-p')].some(x => !x.classList.contains('hide'));
    d.classList.toggle('hide', q && !any);
    if(q) d.open = any;
  });
}

/* ── 池子开关──
   点一下词 = 激活/未激活切换（未激活 = 抽卡机不抽它）。
   改动先记在界面上，点「确认修改」才落盘；保存后像调权重一样，重启抽卡机生效。 */
function togglePi(el){
  const word = el.dataset.en;
  const to = !el.classList.contains('off');
  document.querySelectorAll('#pools-box .pi').forEach(o => {
    if(o.dataset.en === word) o.classList.toggle('off', to);
  });
  if(el.dataset.g === 'characters.FEATURES')
    featOffSet(word, to);
  markPoolsDirty();
}
function markPoolsDirty(){
  $('#pools-dirty').textContent = '● 有未保存的改动';
  $('#pools-save').disabled = false;
}
async function savePoolsOff(){
  const off = {};
  const onWords = new Set();
  document.querySelectorAll('#pools-box .pi:not(.off)').forEach(el => onWords.add(el.dataset.en));
  document.querySelectorAll('#pools-box .pi.off').forEach(el => {
    if(onWords.has(el.dataset.en)) return;
    const g = el.dataset.g;
    (off[g] = off[g] || []).push(el.dataset.en);
  });
  $('#pools-save').disabled = true;
  $('#pools-dirty').textContent = '保存中…';
  try{
    const r = await post('/api/pools/off', {off});
    if(!r || !r.ok) throw new Error((r && r.detail) || '未知错误');
    $('#pools-dirty').textContent = `✅ 已保存 · ${r.total} 条未激活`;
    toast(`已保存 · 抽卡机重启后，这 ${r.total} 条不再被抽到`);
  }catch(e){
    $('#pools-dirty').textContent = '❌ 保存失败';
    $('#pools-save').disabled = false;
    alert('保存失败：' + e.message);
  }
}

const SIZE_MODE_OPTIONS = ['竖优先 1024×1536（六成）', '横优先 1536×1024（六成）',
                           '方优先 1536×1536（六成）'];
let ROLL_PARAMS = null;
async function rollParamsLoad(force){
  if(ROLL_PARAMS && !force) return ROLL_PARAMS;
  try{ ROLL_PARAMS = await api('/api/roll/params'); }catch(e){ /* 端点不在也不崩，回退原逻辑 */ }
  return ROLL_PARAMS;
}
let CF_DATA = null;
async function cfLoad(force){
  if(CF_DATA && !force){ cfRender(); return; }
  try{ CF_DATA = await api('/api/char_filter'); }
  catch(e){ $('#cf-box').innerHTML = `<p class="rp-hint">读不到（${e.message}）</p>`; return; }
  cfRender();
}
function cfFilter(){ cfRender(); }
let CF_OPEN = new Set();
function cfRender(){
  const box = $('#cf-box'); if(!box || !CF_DATA) return;
  if(box.querySelectorAll('details').length){
    box.querySelectorAll('details').forEach(d => {
      const k = d.dataset.wk;
      if(!k) return;
      if(d.open) CF_OPEN.add(k); else CF_OPEN.delete(k);
    });
  }
  const q = (($('#cf-q') && $('#cf-q').value) || '').trim().toLowerCase();
  const works = CF_DATA.works || [];
  let shown = 0;
  const html = works.map(g => {
    const chars = (g.chars || []).filter(c =>
      !q || (c.cn || '').toLowerCase().includes(q) || (c.tag || '').toLowerCase().includes(q));
    if(!chars.length) return '';
    shown += chars.length;
    const onN = chars.filter(c => !c.off).length;
    const chips = chars.map(c =>
      `<span class="pi${c.off ? ' off' : ''}" data-tag="${esc(c.tag)}" title="${esc(c.tag)}"
        onclick="cfToggle(this)">${esc(c.cn || c.tag)}</span>`).join('');
    const _open = q || CF_OPEN.has(String(g.key));
    return `<details class="pool-p" data-wk="${esc(g.key)}"${_open ? ' open' : ''}>
      <summary><span>${esc(g.cn || g.key)}</span>
      <em>${onN}/${chars.length}</em></summary><div class="pool-items">${chips}</div></details>`;
  }).join('');
  box.innerHTML = html || '<p class="rp-hint">没有匹配的角色</p>';
  const n = $('#cf-n');
  if(n) n.textContent = `　出 ${CF_DATA.total - CF_DATA.off_count} / 共 ${CF_DATA.total}`
                      + (q ? ` · 搜到 ${shown}` : '');
}
async function cfToggle(el){
  const tag = el.dataset.tag; if(!tag) return;
  const off = el.classList.contains('off');
  el.classList.toggle('off', !off);
  try{
    await post('/api/char_filter/set', off ? {enable:[tag]} : {disable:[tag]});
    (CF_DATA.works || []).forEach(g => (g.chars || []).forEach(c => { if(c.tag === tag) c.off = !off; }));
    CF_DATA.off_count = (CF_DATA.works || []).reduce((a, g) =>
      a + (g.chars || []).filter(c => c.off).length, 0);
    cfSyncGroupCount(el);
    cfSyncTotal();
  }catch(e){
    el.classList.toggle('off', off);
    toast('保存失败：' + e.message);
  }
}

function cfSyncGroupCount(chipEl){
  const details = chipEl && chipEl.closest('details');
  if(!details) return;
  const chips = details.querySelectorAll('.pi');
  const on = details.querySelectorAll('.pi:not(.off)').length;
  const em = details.querySelector('summary em');
  if(em) em.textContent = `${on}/${chips.length}`;
}

function cfSyncTotal(){
  const n = $('#cf-n'); if(!n || !CF_DATA) return;
  const q = (($('#cf-q') && $('#cf-q').value) || '').trim().toLowerCase();
  const shown = (CF_DATA.works || []).reduce((a, g) => a + (g.chars || [])
    .filter(c => !q || (c.cn || '').toLowerCase().includes(q) || (c.tag || '').toLowerCase().includes(q)).length, 0);
  n.textContent = `　出 ${CF_DATA.total - CF_DATA.off_count} / 共 ${CF_DATA.total}`
                + (q ? ` · 搜到 ${shown}` : '');
}
async function cfAll(on){
  if(!CF_DATA) return;
  const all = [];
  (CF_DATA.works || []).forEach(g => (g.chars || []).forEach(c => all.push(c.tag)));
  if(!all.length) return;
  if(!on && !confirm(`「全不选」= 把 ${all.length} 个角色全部设为不出。\n\n`
      + `（全禁时抽卡机会安全兜底退回全部 —— 所以正确用法是：先全不选，再点亮想要的那几个）\n\n继续？`)) return;
  try{
    await post('/api/char_filter/set', on ? {enable: all} : {disable: all});
    toast(on ? '已全选' : '已全不选（接着点亮你想出的角色）');
    await cfLoad(true);
  }catch(e){ toast('保存失败：' + e.message); }
}

const SIZE_W_KEYS = ['1024x1536', '896x1984', '1536x1024', '1536x1536'];
function applyRollParamsUI(p){
  p = p || {};
  const sw = p.size_weights || {};
  SIZE_W_KEYS.forEach(k => {
    const el = $('#rc-sw-' + k);
    if(el && sw[k] !== undefined && sw[k] !== null) el.value = String(sw[k]);
  });
  const hint = $('#rc-params-hint');
  if(hint){
    const tot = SIZE_W_KEYS.reduce((a, k) => a + (parseFloat(sw[k]) || 0), 0);
    const pct = SIZE_W_KEYS.map(k => {
      const v = parseFloat(sw[k]) || 0;
      return `${k} ${tot > 0 ? Math.round(v / tot * 100) : 0}%`;
    }).join(' · ');
    hint.textContent = `当前比例：${pct}　（步数 12 · 种子随机 · 每日上限 ${p.daily_cap} 张）`;
  }
}
function syncSeedInput(){}

async function refreshRoll(){
  try{
    const d = await api('/api/roll/status');
    $('#roll-run').textContent = d.stopping ? '⏳ 等这张画完…' : (d.running ? '🟢 运行中' : '⚪ 已停止');
    $('#roll-state').textContent = d.stopping ? '停止中' : (d.running ? '运行中' : '已停止');
    const _dl = d.daily || {};
    const _capTxt = (_dl.cap > 0 || _dl.hard > 0)
      ? ` · 今日 ${_dl.n}` + (_dl.cap > 0 ? `／软 ${_dl.cap}` : '') + (_dl.hard > 0 ? `／硬 ${_dl.hard}` : '')
        + (_dl.hard_hit ? ' ⛔ **已到硬上限，产线今天停工**（重抽照常）'
           : (_dl.paused ? ' ⏸ **已自动停**（点「启动」可继续，今天不再自动停）'
              : (_dl.override ? ' （今天已手动解除软上限 ✓）' : '')))
      : '';
    $('#roll-today').textContent = `${d.today} 张（${d.day}）${_capTxt}`;
    const c = d.config || {};
    const rp = await rollParamsLoad(true);
    if(rp && rp.params) applyRollParamsUI(rp.params);
    applyRollParamsUI(Object.assign({}, (ROLL_PARAMS && ROLL_PARAMS.params) || {},
                                    {size_weights: c.size_weights || {}}));
    if($('#rc-cap')) $('#rc-cap').value = String((c.daily_cap !== undefined && c.daily_cap !== null) ? c.daily_cap : 100);
    if($('#rc-caphard')) $('#rc-caphard').value = String((c.daily_cap_hard !== undefined && c.daily_cap_hard !== null) ? c.daily_cap_hard : 200);
    {
      const tw = c.tier_weights || {};
      ['fashion','tease','exposed','sex'].forEach(k => {
        const el = $('#tw-' + k);
        if(el) el.value = (tw[k] !== undefined && tw[k] !== null) ? tw[k] : 0;
      });
    }
    $('#roll-log').textContent = (d.log || '').trim() || '（无日志）';
    try{ cfLoad(); }catch(e){}
    window.scrollTo(0,0);
  }catch(e){ toast('读取失败：' + e.message); }
}
async function rollCtl(a){
  const label = {start:'启动', stop:'停止', restart:'重启'}[a] || a;
  if(a === 'stop' && !confirm('停止抽卡机？（会**等正在画的那张画完**再停）')) return;
  toast('正在' + label + '…');
  const r = await post('/api/roll/ctl', {action:a});
  if(!r.ok){ alert(label + '失败：' + (r.detail || '未知错误')); return; }
  if(r.stopping){
    toast('⏳ 等这张画完就停…');
    rollWaitStopped();
    return;
  }
  toast(r.running ? '🟢 抽卡机运行中' : '⚪ 抽卡机已停止');
  setTimeout(refreshRoll, 800);
}
async function rollWaitStopped(){
  const t0 = Date.now();
  while(Date.now() - t0 < 30*60*1000){
    await new Promise(res => setTimeout(res, 3000));
    let d;
    try{ d = await api('/api/roll/status'); }catch(e){ continue; }
    if(!d.running){
      toast('⚪ 抽卡机已停止（当前那张已画完）');
      refreshRoll(); return;
    }
    $('#roll-run').textContent = '⏳ 等这张画完…';
    $('#roll-state').textContent = '停止中';
  }
  toast('⚠️ 等了 30 分钟还没停，去看看吧');
  refreshRoll();
}
async function saveRollConfig(){
  const sw = {};
  SIZE_W_KEYS.forEach(k => {
    const el = $('#rc-sw-' + k);
    sw[k] = el ? Math.max(0, parseFloat(el.value) || 0) : 0;
  });
  if(!SIZE_W_KEYS.some(k => sw[k] > 0)){ toast('比例至少要有一项大于 0'); return; }
  const body = {
    daily_cap: +$('#rc-cap').value,
    daily_cap_hard: $('#rc-caphard') ? +$('#rc-caphard').value : 0,
    size_weights: sw,
  };
  if(body.daily_cap_hard > 0 && body.daily_cap > 0 && body.daily_cap_hard <= body.daily_cap){
    toast('硬上限要大于软上限（软 ' + body.daily_cap + ' / 硬 ' + body.daily_cap_hard + '）');
    return;
  }
  await post('/api/roll/config', body);
  toast('✅ 已保存，点「🔄 重启」生效');
}
async function saveEquipConfig(){
  const body = { tier_weights: {
    fashion: +$('#tw-fashion').value, tease: +$('#tw-tease').value,
    exposed: +$('#tw-exposed').value, sex: +$('#tw-sex').value,
  }};
  await post('/api/roll/config', body);
  toast('✅ 权重已保存，点抽卡机里的「🔄 重启」生效');
}

async function quickAction(kind){
  const p = ALL[CUR]; if(!p) return;
  if(kind === 'style'){ openStylePanel(); return; }
  const label = kind === 'split' ? '拆分·设定图' : '更进一步';
  const tip = kind === 'split'
      ? '加部位标签 + 去环境描述 + 强制横屏（出多视角设定图）'
      : '亲密度推进一级（无漏→脱衣→露点→勾引→自慰→做爱→高潮→射精→事后）';
  if(!confirm(`对这张执行「${label}」？\n\n· ${tip}\n· 按原种子重画（服装、构图基本不变）\n· 结果放进「重抽_今天」相册`)) return;
  closeRepaint();
  toast(`已提交「${label}」…`);
  const r = await post('/api/redraw', {rel: p.rel, quick: kind});
  if(r.error){ alert(label + '失败：' + r.error); return; }
  pollRedraw(r.job);
}

let STYLE_OPTS = null;
async function openStylePanel(){
  const p = ALL[CUR]; if(!p){ toast('先选一张图'); return; }
  closeRepaint();
  try{
    const r = await api('/api/styles');
    STYLE_OPTS = (r && r.styles) || [];
  }catch(e){ STYLE_OPTS = null; }
  if(!STYLE_OPTS || !STYLE_OPTS.length){ alert('拿不到画风清单（后端没在跑？）'); return; }
  $('#sp-list').innerHTML = STYLE_OPTS.map(o =>
      `<button onclick="pickStyle('${esc(o.key)}')">${esc(o.label)}</button>`).join('');
  $('#stylepanel').classList.add('show');
}
function closeStylePanel(){ $('#stylepanel').classList.remove('show'); }
async function pickStyle(k){
  const p = ALL[CUR]; if(!p) return;
  closeStylePanel();
  toast(`已提交「换成 ${k}」…`);
  const r = await post('/api/redraw', {rel: p.rel, quick: 'style', style: k});
  if(r.error){ alert('换画风失败：' + r.error); return; }
  pollRedraw(r.job);
}

function openPicker(){
  if(!PKCAT) PKCAT = TAGLIB.categories[0] ? TAGLIB.categories[0].key : '';
  $('#tp-q').value = '';
  $('#tagpicker').classList.add('show');
  renderPicker();
}
function closePicker(){ $('#tagpicker').classList.remove('show'); renderRPTags(); updateRPHint(); }
function pickCat(k){ PKCAT = k; renderPicker(); }
function toggleTag(en){
  const feats = CHAR_FEATS_MAP[en];
  if(feats){
    const on = RP.tags.indexOf(en) < 0;
    if(on){
      if(!RP.tags.includes(en)) RP.tags.push(en);
      feats.forEach(f => { if(!RP.tags.includes(f)) RP.tags.push(f); });
    }else{
      const shared = new Set();
      Object.keys(CHAR_FEATS_MAP).forEach(other => {
        if(other !== en && RP.tags.includes(other)) CHAR_FEATS_MAP[other].forEach(f => shared.add(f));
      });
      RP.tags = RP.tags.filter(t => t !== en && (!feats.includes(t) || shared.has(t)));
    }
  }else{
    const i = RP.tags.indexOf(en);
    if(i >= 0) RP.tags.splice(i, 1); else RP.tags.push(en);
  }
  renderPicker();
}
function renderPicker(){
  const cats = TAGLIB.categories || [];
  const isV3 = cats.some(c => c.subs);
  const q = ($('#tp-q').value || '').trim().toLowerCase();
  const esc1 = (x) => String(x).replace(/'/g, "\\'");
  const bg = (i) => (i && i.c) ? ` style="background:${i.c};border-color:${i.c}"` : '';

  if(!isV3){                       
    if(!PKCAT && cats[0]) PKCAT = cats[0].key;
    $('#tp-tabs').innerHTML = cats.map(c =>
      `<span class="chip${c.key === PKCAT ? ' on' : ''}" onclick="pickCat('${c.key}')">${c.label}</span>`).join('');
    let list = cats;
    if(!q){ list = cats.filter(c => c.key === PKCAT); }
    $('#tp-list').innerHTML = list.map(c => {
      const its = (c.items || []).filter(i => !q ||
        i.en.toLowerCase().includes(q) || (i.cn || '').includes(q));
      if(!its.length) return '';
      return `<div class="rp-grp"><h4>${c.label} · ${its.length}</h4><div class="rp-tags">` +
        its.map(i => `<span class="tg${tgClass(i.en)}${RP.tags.includes(i.en) ? ' on' : ''}" onclick="toggleTag('${esc1(i.en)}')" title="${i.en}">${i.cn || i.en}</span>`).join('') +
        '</div></div>';
    }).join('') || '<p class="rp-hint">没有匹配的标签</p>';
    $('#tp-sel').textContent = `已选 ${RP.tags.length} 个标签`;
    return;
  }

  if(!PKCAT && cats[0]) PKCAT = cats[0].key;
  const cur = cats.find(c => c.key === PKCAT) || cats[0];

  $('#tp-tabs').innerHTML = cats.map(c =>
    `<span class="chip${c.key === PKCAT ? ' on' : ''}" onclick="pickCat('${c.key}')">${c.icon || ''}${c.label}</span>`).join('');

  const _isChar = (i) => !!(i && i.k === 'char');
  const chip = (i) => `<span class="tg${tgClass(i.en)}${_isChar(i) ? ' tg-char' : ''}${RP.tags.includes(i.en) ? ' on' : ''}"${_isChar(i) ? '' : bg(i)}` +
    ` onclick="toggleTag('${esc1(i.en)}')" title="${i.en}">${i.cn || i.en}</span>`;

  if(q){                            
    let hits = [];
    cats.forEach(c => (c.subs || []).forEach(sub =>
      (sub.items || []).forEach(i => {
        if(i.en.toLowerCase().includes(q) || (i.cn || '').includes(q)) hits.push(chip(i));
      })));
    $('#tp-list').innerHTML = hits.length
      ? `<div class="rp-grp"><h4>搜索 · ${hits.length}</h4><div class="rp-tags">${hits.join('')}</div></div>`
      : '<p class="rp-hint">没有匹配的标签</p>';
  } else {
    const subs = (cur && cur.subs) || [];
    $('#tp-list').innerHTML = subs.map(sub =>
      `<div class="rp-grp"><h4>${sub.label} · ${(sub.items || []).length}</h4><div class="rp-tags">` +
      (sub.items || []).map(chip).join('') + '</div></div>').join('')
      || '<p class="rp-hint">这个大类还没有词条</p>';
  }
  $('#tp-sel').textContent = `已选 ${RP.tags.length} 个标签`;
}

function openToolMenu(){
  const m = $('#tool-menu');
  const opening = !m.classList.contains('show');
  m.classList.toggle('show');
  if(!opening) return;

  const inst = $('#tm-install');
  if(inst && /iPad|iPhone|iPod/.test(navigator.userAgent)) inst.style.display = 'flex';

  api('/api/redraw_active').then(r => {
    const n = (r && r.queued) || 0;
    const el = $('#tm-qn'); if(el) el.textContent = n ? `（${n} 个在等）` : '';
  }).catch(() => {});
  refreshMachineLamps();          
}

async function refreshMachineLamps(){
  let d;
  try { d = await api('/api/roll/status'); } catch(e) { return; }
  const { run } = machineState(d);
  const g = { equip: run };
  const set = (id, lamp, on) => {
    const it = document.getElementById(id);
    if(it) it.classList.toggle('on', !!on);
    const l = document.getElementById(lamp);
    if(l) l.classList.toggle('on', !!on);
  };
  set('tm-roll',  'tm-lamp-roll',  run);
  set('tm-equip', 'tm-lamp-equip', g.equip);
}
function menuPick(what){
  $('#tool-menu').classList.remove('show');

  if(what === 'equip'){ toast('🚧 装备机维护中 —— 尺度权重已并入抽卡机设置页'); return; }
  if(what === 'roll') openRollPanel();
  else openQueuePanel();
}

document.addEventListener('click', e => {
  const m = $('#tool-menu');
  if(!m || !m.classList.contains('show')) return;
  if(e.target.closest('#tool-menu') || e.target.closest('#rd-badge')) return;
  m.classList.remove('show');
});

let DEFERRED_INSTALL = null;
const _isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  DEFERRED_INSTALL = e;
  const el = document.getElementById('tm-install');
  if(el) el.style.display = 'flex';
});
window.addEventListener('appinstalled', () => {
  DEFERRED_INSTALL = null;
  toast('✅ 已安装到桌面');
  const el = document.getElementById('tm-install');
  if(el) el.style.display = 'none';
});
async function pickInstall(){
  $('#tool-menu').classList.remove('show');
  if(DEFERRED_INSTALL){
    DEFERRED_INSTALL.prompt();
    try{
      const r = await DEFERRED_INSTALL.userChoice;
      if(r && r.outcome === 'accepted') toast('正在安装…');
    }catch(e){}
    DEFERRED_INSTALL = null;
    const el = document.getElementById('tm-install');
    if(el) el.style.display = 'none';
    return;
  }
  alert(_isIOS
    ? 'iPhone 安装方式（必须用 Safari）：\n\n'
    + '1. 用 Safari 打开这个页面\n'
    + '2. 点底部中间的「分享」按钮（方框+向上箭头）\n'
    + '3. 往下找到「添加到主屏」\n'
    + '4. 右上角「添加」\n\n'
    + '注意：Chrome、微信内置浏览器都没有这个选项，这是苹果的限制。'
    : '没检测到可安装状态。可能的原因：\n\n'
    + '· 已经安装过了\n'
    + '· 浏览器不支持（用 Chrome / Edge 试试）\n'
    + '· 页面还没刷到最新版（强刷一次，看版本号是不是 v32.7）\n'
    + '· Chrome 菜单里请选「安装」而不是「创建快捷方式」');
}

function idleBadge(){                    
  const b = $('#rd-badge'); if(!b) return;
  b.classList.remove('done', 'running');
  b.textContent = '⚙️';
  b.title = '抽卡机 / 重抽队列';
}
function setRedrawBadge(jid, st){
  const b = $('#rd-badge'); if(!b) return;
  if(!st || st.status === 'running' || st.status === 'queued'){
    b.classList.remove('done');
    b.classList.add('running');          
    b.textContent = '🔁';
    const qn = (st && st.queued) || 0;
    const last = ((st && st.log) || []).slice(-1)[0] || '';
    b.title = `重抽中 ${(st && st.done) || 0}/${(st && st.total) || '?'}`
            + (qn ? `（队列还有 ${qn} 个）` : '') + (last ? `\n${last}` : '');
  } else if(st.status === 'done'){
    b.classList.add('done');
    b.classList.remove('running');
    b.textContent = '✅';
    b.title = `已完成 ${st.files ? st.files.length : 0} 张`;
    setTimeout(() => idleBadge(), 5000);
  } else {
    b.classList.add('done');
    b.classList.remove('running');
    b.textContent = '⚠️';
    b.title = st.error || '重抽失败';
    setTimeout(() => idleBadge(), 8000);
  }
}
async function resumeRedraw(){

  try{
    const r = await api('/api/redraw_active');
    if(r && r.job){ setRedrawBadge(r.job, r); pollRedraw(r.job, true); }
    else if(r && r.queued){ showQueueBadge(r.queued); }
    else { idleBadge(); }        
  }catch(e){ idleBadge(); }
}
function showQueueBadge(n){                                
  const b = $('#rd-badge'); if(!b) return;
  b.classList.remove('done');
  b.classList.add('running');
  b.textContent = '🔁';
  b.title = `队列里还有 ${n} 个重抽任务在等`;
}
function pollRedraw(jid, quiet){
  const tick = setInterval(async () => {
    const st = await api('/api/redraw_status?job=' + jid);
    if(st.status === 'queued'){                
      setRedrawBadge(jid, st);
      return;        
    }
    setRedrawBadge(jid, st);
    if(st.status === 'running'){

    }
    else {
      clearInterval(tick);
      if(st.status === 'done'){
        toast(`✅ 重抽完成 ${st.files.length} 张，已放入 ${st.outdir}`);
        _needReload = true;                 
        if(!$('#viewer').classList.contains('show')){ _needReload = false; load(); }
        else { const pp = ALL[CUR]; if(pp) loadVersions(pp.rel); }
      } else {
        alert('重抽失败：' + (st.error || (st.log||[]).join('\n')));
      }
    }
  }, 3000);
}
async function submitRepaint(){
  const p = ALL[CUR]; if(!p) return;
  const prompt = rpPrompt();
  if(!prompt){ alert('提示词不能为空'); return; }
  const [w, h] = $('#rp-size').value.split('x');
  const body = {rel:p.rel, prompt, width:+w, height:+h,
                steps:+$('#rp-steps').value, count:+$('#rp-count').value,
                seed_mode:$('#rp-seed').value};
  closeRepaint();          
  toast('已提交重抽…');
  const r = await post('/api/redraw', body);
  if(r.error){ alert('无法重抽：' + r.error); return; }
  if(r.position > 0) toast(`⏳ 已排队（前面还有 ${r.position - 1} 个），轮到会自动开跑`);
  pollRedraw(r.job);
}
async function actRedraw(){ return openRepaint('newseed'); }

async function actQuickRedraw(){
  const p = ALL[CUR]; if(!p) return;
  if(!p.prompt){ alert('日志里没有这张的提示词，无法重抽'); return; }
  const [w, h] = (p.size || '1024x1536').split('x');
  toast('🎲 快抽中…（原参数 + 随机种子，1 张）');
  const r = await post('/api/redraw', {rel:p.rel, width:+w, height:+h,
                                       steps:p.steps || 8, count:1, seed_mode:'random'});
  if(r.error){ alert('无法重抽：' + r.error); return; }
  if(r.position > 0) toast(`⏳ 已排队（前面还有 ${r.position - 1} 个），轮到会自动开跑`);

  pollRedraw(r.job);
}
async function actDelete(){
  const p = ALL[CUR]; if(!p) return;
  if(!confirm('把这张移到废纸篓？\n\n' + p.name + '\n\n(移到 macOS 废纸篓，不是永久删除，随时能恢复)')) return;

  const vrel = [...document.querySelectorAll('#v-versions .vthumb')].map(e => e.dataset.rel);
  const vi = vrel.indexOf(p.rel);
  const nextVerRel = vi >= 0 ? (vrel[vi + 1] || vrel[vi - 1] || null) : null;
  const r = await post('/api/delete', {paths:[p.rel]});
  if(r.moved){
    toast('已移到废纸篓');
    ALL.splice(CUR, 1);
    if(!ALL.length){ closeViewer(); return; }

    let idx = -1;
    if(nextVerRel && nextVerRel !== p.rel) idx = ALL.findIndex(x => x.rel === nextVerRel);
    if(idx < 0) idx = Math.min(CUR, ALL.length - 1);
    CUR = idx;
    _needReload = true;                 
    renderViewer();
    const _pp = ALL[CUR];
    if(_pp && $('#v-versions').style.display !== 'none') loadVersions(_pp.rel);
  } else {
    alert('删除失败: ' + JSON.stringify(r.failed));
  }
}
async function actTag(){
  const p = ALL[CUR]; if(!p) return;
  const t = prompt('给这张打标签（逗号分隔；留空清空）：', (p.tags||[]).join(','));
  if(t === null) return;
  const tags = t.split(/[,，]/).map(x=>x.trim()).filter(Boolean);
  await post('/api/tags', {paths:[p.rel], add:tags, clear: tags.length===0});
  p.tags = tags; toast('标签已更新');
  const f = await api('/api/facets'); renderTagChips(f.tags||[]);
  load();
}

async function syncFavOf(p){
  if(!p || !p.rel) return;
  try{
    const r = await api('/api/fav/get?rel=' + encodeURIComponent(p.rel));
    if(r && typeof r.fav === 'boolean' && r.fav !== !!p.fav){
      p.fav = r.fav;
      renderViewer();
      syncThumbFav(p.rel, r.fav);
    }
  }catch(e){}
}
async function actFav(){
  const p = ALL[CUR]; if(!p) return;
  const v = !p.fav;                       
  await post('/api/fav', {paths:[p.rel], value:v});
  p.fav = v;
  toast(v ? '⭐ 已收藏' : '☆ 已取消收藏');
  renderViewer();                          
  syncThumbFav(p.rel, v);                  
}

boot();

addEventListener('load', () => {
  const q = new URLSearchParams(location.search);

  const alb = q.get('album');
  if(alb) setTimeout(() => { if(typeof STATE !== 'undefined'){ STATE.album = alb;
      const el = $('#f-album'); if(el) el.value = alb; load(); } }, 400);
  if(q.get('vmulti') === '1'){
    setTimeout(() => { const g = $('#grid');
      [...g.children].forEach(el => { if(!el.querySelector('.vbadge')) el.remove(); });
      const c = $('#cnt'); if(c) c.textContent = `(只看多版本 · ${g.children.length} 张)`;
    }, 1200);
  }
  const p = q.get('panel');
  if(!p) return;
  setTimeout(async () => {

    if(p === 'queue'){ await openQueuePanel(); return; }
    if(p === 'equip' || p === 'pools'){
      await openEquipPanel();                    
      if(p === 'pools'){
        await loadPools();                       
        const open = q.get('open') === 'all';
        document.querySelectorAll('#pools-box details').forEach(d => d.open = open);
      }
      return;
    }
    await openRollPanel();                       
  }, 150);
});

if('serviceWorker' in navigator){ navigator.serviceWorker.register('/sw.js').catch(()=>{}); }

const GACHA_PRE_NSFW = 'masterpiece, best quality, uncensored, ecchi';   
const GACHA_PRE_SAFE = 'masterpiece, best quality, safe, fashion';       
let GACHA_PRE = GACHA_PRE_SAFE;        
function gcPre(){
  const t = GC_SEL.tier;
  const safe = (!t || t === GC_EMPTY || t === 'fashion' || t === 'general');
  return safe ? GACHA_PRE_SAFE : GACHA_PRE_NSFW;
}
const GACHA_SUF  = 'year 2025';
function gcPromptRaw(){ return ($('#gc-prompt').value || '').trim(); }
function gcResetFix(){
  GC_MANUAL = '';                       
  gcSetPrompt(gcPre() + ', ' + GACHA_SUF);
  gcHint();
}
function gcHint(){
  const n = gcPromptRaw().split(',').filter(x => x.trim()).length;
  $('#gc-hint').textContent = `当前 ${n} 个词 · 固定词已含在里面（删掉就不会带）`;
  gcGuessTier();
}

let _gcGuessT = null;
function gcGuessTier(){
  clearTimeout(_gcGuessT);
  _gcGuessT = setTimeout(async () => {
    const el = $('#gc-tier'); if(!el) return;
    try{
      const d = await post('/api/tier_guess', {prompt: gcPromptRaw()});
      const pos = (d.tier === 'sex' && posCN(d.action)) ? ' · ' + posCN(d.action) : '';
      el.textContent = '预计档位：' + tierCN(d.tier) + pos;
    }catch(e){ el.textContent = ''; }
  }, 350);
}

const GC_POSE_CATS = [

  {k: '##stand', label: '站着', re: /standing|stand|stance|gait|leaning/},
  {k: '##sit',   label: '坐着', re: /sitting|seated|reclining|squatting|upright/},
  {k: '##lie',   label: '躺着', re: /lying|on her back|on her side|supine|sprawled|fetal/},
  {k: '##kneel', label: '跪着', re: /kneel/},
  {k: '##bend',  label: '趴着', re: /all fours|prone|bent|crouch|stomach/},
];
const GC_SLOTS = [
  {k: 'work',   label: '作品', src: '__works', filter: true},
  {k: 'char',   label: '角色', src: 'char',    by: 'work'},
  {k: 'tier',   label: '尺度', src: '__tiers', filter: true},
  {k: 'pose',   label: '姿态', src: '__posecat'},   
  {k: 'outfit', label: '服装', src: 'outfit', auto: true, srv: 1},   
  {k: 'scene',  label: '场景', src: 'scene'},

  {k: 'hand',   label: '手部', src: 'hand',   auto: true, srv: 1},
  {k: 'leg',    label: '腿部', src: 'leg',    auto: true, srv: 1},
  {k: 'head',   label: '视线', src: 'head',   auto: true, srv: 1},
  {k: 'mood',   label: '表情', src: 'mood',   auto: true, srv: 1},
  {k: 'light',  label: '光线', src: 'light',  auto: true, srv: 1},   
  {k: 'camera', label: '机位', src: 'camera', auto: true, srv: 1},   
];

const GC_EMPTY_DEF = '__empty__', GC_RAND_DEF = '__rand__';
const GC_DEFAULTS = {
  work: '__empty__', char: '__rand__', tier: '__empty__', pose: '__rand__',
  outfit: '__rand__', scene: '__rand__', camera: '__rand__', light: '__rand__',
  hand: '__rand__', leg: '__rand__', head: '__rand__', mood: '__rand__',
};
const GC_EMPTY = GC_EMPTY_DEF, GC_RAND = GC_RAND_DEF;
let GC_SEL = {};          
let GC_RES = {};          
let GC_MANUAL = '';       
let _gcSilent = false;    

function gcSlotSrc(s) {
  if (s.k === 'scene')  return (GC_SEL.tier === 'sex') ? 'eq_scene' : 'scene';
  return s.src;
}
function gcPoseItems() {

  const cats = TAGLIB.categories || [];
  const c = cats.find(x => x.key === 'pose');
  if (c && c.items) return c.items;                  
  const big = cats.find(x => x.label === '姿态');     
  if (big && big.subs) {
    const p = big.subs.find(x => (x.from || []).includes('pose')) || big.subs.find(x => x.label === '姿势 · 日常');
    return (p && p.items) || [];
  }
  return [];
}
function gcPosesOf(cat) {                     
  const all = gcPoseItems();
  if (!cat || cat === GC_RAND || cat === GC_EMPTY) return all;
  const c = GC_POSE_CATS.find(x => x.k === cat);
  if (!c) return all;
  const hit = all.filter(i => c.re.test(String(i.en || '').toLowerCase()));
  return hit.length ? hit : all;
}
function gcSlotPool(s) {
  const d = TAGLIB || {};
  let items;
  if (s.srv) return [];          
  if (s.src === '__posecat') {
    return GC_POSE_CATS.map(c => ({en: c.k, cn: c.label}));   
  }
  if (s.src === '__works') {
    items = Object.entries(d.works || {}).map(([en, cn]) => ({en, cn}));
  } else if (s.src === '__tiers') {
    items = Object.entries(d.tier_classes || {}).map(([en, cn]) => ({en, cn}));
  } else {

    const _V3MAP = { char: 'L02', scene: 'L06', outfit: 'L04' };   
    const _SUBKEY = { char: 'char_name',                            
                      scene: 'scene_place', eq_scene: 'scene_place' };  
    const _LBLKW  = { char: '角色', scene: '场景', outfit: '装备' };  
    const _want = gcSlotSrc(s);
    const _cats = d.categories || [];
    const _hitSub = (name) => {
      for (const c of _cats) {
        for (const x of (c.subs || [])) if (x.key === name) return x;
      }
      return null;
    };

    const cat = _cats.find(c => c.key === _want)
             || _cats.find(c => c.key === _V3MAP[_want])
             || null;
    let sub = _hitSub(_want) || _hitSub(_SUBKEY[_want] || '');
    if (!cat && !sub) {
      const kw = _LBLKW[_want];
      const c2 = kw && _cats.find(c => String(c.label || '').includes(kw)
                                       && ((c.items || []).length || (c.subs || []).length));
      if (c2) sub = (c2.subs || [])[0] || null;
    }
    const src = sub && (sub.items || []).length ? sub.items
              : (cat ? (cat.items || []) : []);
    items = src.map(i => ({en: i.en, cn: i.cn || i.en}));
  }
  if (s.by === 'work') {                       
    const w = GC_SEL.work;
    if (w && w !== GC_EMPTY && w !== GC_RAND) {
      const cw = d.char_works || {};
      items = items.filter(i => cw[i.en] === w);
    }
  }
  const seen = new Set(), out = [];            
  for (const it of items) {
    const key = String(it.cn || it.en).trim();
    if (seen.has(key)) continue;
    seen.add(key); out.push(it);
  }
  return out;
}
function gcSlotDisabled(s) {

  return false;
}
function gcResolveSel(reroll) {
  for (const s of GC_SLOTS) {
    const v = GC_SEL[s.k] || GC_EMPTY;
    if (s.srv && s.src !== '__posecat') continue;   
    if (s.src === '__posecat') {              
      if (v === GC_EMPTY) { GC_RES[s.k] = ''; continue; }
      const pool = (v === GC_RAND) ? gcPoseItems() : gcPosesOf(v);
      const keep = GC_RES[s.k] && pool.some(i => i.en === GC_RES[s.k]);
      if (reroll || !keep) {
        GC_RES[s.k] = pool.length ? pool[Math.floor(Math.random() * pool.length)].en : '';
      }
      continue;
    }
    if (s.filter || v === GC_EMPTY) { GC_RES[s.k] = ''; continue; }
    if (v === GC_RAND) {
      if (reroll || GC_RES[s.k] === undefined) {
        const p = gcSlotPool(s);
        GC_RES[s.k] = p.length ? p[Math.floor(Math.random() * p.length)].en : '';
      }
    } else { GC_RES[s.k] = v; }
  }
}
function gcSetPrompt(v) { _gcSilent = true; $('#gc-prompt').value = v; _gcSilent = false; }
function gcSyncManual() {                      
  let t = ' ' + ($('#gc-prompt').value || '') + ' ';
  const strip = [GACHA_PRE_NSFW, GACHA_PRE_SAFE, GACHA_SUF].concat(
    GC_SLOTS.map(s => GC_RES[s.k]).filter(Boolean));
  for (const seg of strip) { if (seg) t = t.split(seg).join(' , '); }
  GC_MANUAL = t.split(',').map(x => x.trim()).filter(Boolean).join(', ');
}
function gcCompose() {
  const parts = GC_SLOTS.map(s => GC_RES[s.k]).filter(Boolean);
  const bits = [gcPre()].concat(parts);
  if (GC_MANUAL.trim()) bits.push(GC_MANUAL.trim());
  gcSetPrompt(bits.filter(Boolean).join(', ') + ', ' + GACHA_SUF);
}
let GC_AUTO_ON = true;
function gcApplyDefaults() {                  
  GC_SLOTS.forEach(s => {
    if (GC_SEL[s.k] === undefined) GC_SEL[s.k] = GC_DEFAULTS[s.k] || GC_EMPTY;
  });
}
function gcToggleAuto() {
  GC_AUTO_ON = !GC_AUTO_ON;
  const v = GC_AUTO_ON ? GC_RAND : GC_EMPTY;
  GC_SLOTS.filter(s => s.auto).forEach(s => { GC_SEL[s.k] = v; GC_RES[s.k] = undefined; });
  gcRenderSel(false);
  const b = $('#gc-auto');
  if (b) b.textContent = '🪄 自动补满：' + (GC_AUTO_ON ? '开' : '关');
}
const GC_SRV = ['pose', 'hand', 'leg', 'head', 'mood', 'light', 'camera', 'outfit'];
let _gcFillSeq = 0;

async function gcServerFill(reroll) {

  const want = {};
  const cats = {pose: GC_SEL.pose, hand: GC_SEL.hand, leg: GC_SEL.leg,
                head: GC_SEL.head, mood: GC_SEL.mood, light: GC_SEL.light,
                camera: GC_SEL.camera, outfit: GC_SEL.outfit};
  let any = false;
  for (const k of GC_SRV) {
    const v = cats[k] || GC_EMPTY;
    if (v === GC_EMPTY) { GC_RES[k] = ''; continue; }
    if (k === 'pose' ? true : v === GC_RAND) { want[k] = true; any = true; }
  }
  if (!any) return;
  const seq = ++_gcFillSeq;
  try {
    const d = await post('/api/gacha/fill', {
      pose_cat: cats.pose === GC_RAND ? '##rand' : (cats.pose === GC_EMPTY ? '' : cats.pose),
      tier: GC_SEL.tier === GC_EMPTY ? '' : (GC_SEL.tier || ''),
      want, reroll: !!reroll,
    });
    if (seq !== _gcFillSeq) return;              
    const sl = d.slots || {};
    for (const k of GC_SRV) { if (k in sl) GC_RES[k] = sl[k]; }
  } catch (e) {  }
  gcCompose(); gcPaintSel();
}

function gcRenderSel(reroll) {
  const box = $('#gc-sel'); if (!box) return;
  gcResolveSel(reroll);      
  gcPaintSel();
  gcCompose(); gcHint();
  gcServerFill(reroll);      
}

function gcPaintSel() {
  GC_SLOTS.forEach(s => {
    const sel = $('#gcs-' + s.k); if (!sel) return;
    const pool = gcSlotPool(s);
    const cur = GC_SEL[s.k] || GC_EMPTY;
    const keep = sel.innerHTML;
    sel.innerHTML = `<option value="${GC_EMPTY}">— 留空 —</option>`
      + `<option value="${GC_RAND}">🎲 随机</option>`
      + pool.map(i => `<option value="${esc(i.en)}">${esc(i.cn)}</option>`).join('');
    sel.value = pool.some(i => i.en === cur) || cur === GC_RAND || cur === GC_EMPTY
      ? cur : GC_EMPTY;
    if (sel.value !== cur) { GC_SEL[s.k] = sel.value; }
    const dis = gcSlotDisabled(s);
    sel.disabled = dis;
    sel.closest('.gcs-item').classList.toggle('gcs-off', dis);
  });

  const chips = [];
  for (const s of GC_SLOTS) {
    const v = GC_SEL[s.k] || GC_EMPTY;
    if (v === GC_EMPTY) continue;
    let txt = v === GC_RAND ? '🎲随机' : (GC_RES[s.k] || GC_SEL[s.k]);
    const cn = (TAGLIB.cn || {})[GC_RES[s.k]];
    if (cn && !s.filter) txt = cn;
    if (s.src === '__posecat' && GC_RES[s.k]) {          
      const cat = (GC_POSE_CATS.find(x => x.k === v) || {}).label || '随机';
      txt = `${cat} → ${cn || GC_RES[s.k]}`;
    }
    if (s.src === '__works') txt = (TAGLIB.works || {})[v] || v;
    if (s.src === '__tiers') txt = (TAGLIB.tier_classes || {})[v] || v;
    chips.push(`<span class="gcs-chip">${esc(s.label)}：<b>${esc(txt)}</b>${s.filter ? '（只筛）' : ''}</span>`);
  }
  const h = $('#gc-sel-hint');
  if (h) h.innerHTML = chips.length
    ? `<span class="gcs-sum">${chips.join('')}</span>`
    : '<span style="color:var(--fg2)">还没选。作品/尺度只用来筛后面；其余选中会直接写进上面的提示词 ✓</span>';
}
function gcSelReroll() { gcRenderSel(true); }
function gcSelClear() {
  GC_SEL = {}; GC_RES = {};
  gcRenderSel(false);
}
function gcBuildSel() {
  const box = $('#gc-sel'); if (!box || box.dataset.built) return;
  box.innerHTML = GC_SLOTS.map(s =>
    `<div class="gcs-item${s.filter ? ' fi' : ''}">
       <label>${esc(s.label)}${s.filter ? '<b>·筛</b>' : ''}</label>
       <select id="gcs-${s.k}" data-k="${s.k}"></select>
     </div>`).join('');
  box.addEventListener('change', e => {
    const k = e.target.dataset.k; if (!k) return;
    GC_SEL[k] = e.target.value;
    if (k === 'work') { GC_SEL.char = GC_EMPTY; GC_RES.char = undefined; }  
    gcRenderSel(false);
  });
  box.dataset.built = '1';
}

async function openGacha(){

  try{ closeRollPanel(); }catch(e){}
  try{ closeQueuePanel(); }catch(e){}
  try{ document.querySelectorAll('#tool-menu,.menu').forEach(m => m.classList.remove('show')); }catch(e){}
  const sz = ['1024x1536','1536x1024','1536x1536','512x768','700x1050'];
  $('#gc-size').innerHTML  = sz.map(x => `<option value="${x}">${x}</option>`).join('');
  $('#gc-size').value = '1024x1536';
  $('#gc-steps').innerHTML = Array.from({length:9}, (_, i) => i + 4)
    .map(n => `<option value="${n}">${n} 步</option>`).join('');
  $('#gc-steps').value = '8';
  $('#gc-count').innerHTML = [1,2,3,4].map(n => `<option value="${n}">${n} 张</option>`).join('');
  $('#gc-count').value = '1';
  if(!$('#gc-prompt').value) gcResetFix();

  $('#gc-prompt').oninput = () => { if(!_gcSilent){ gcSyncManual(); } gcHint(); };
  gcBuildSel();
  gcApplyDefaults();          
  $('#gachapanel').classList.add('show');
  $('#gachapanel').scrollTop = 0;
  await gcRenderTags();       
  gcRenderSel(false);         
  myTagsLoad();
}
function closeGacha(){ $('#gachapanel').classList.remove('show'); }
function gcLegend(){
  return '<div class="tg-legend"><span style="color:var(--fg2)">颜色＝尺度：</span>'
    + ['general','fashion','tease','exposed','sex'].map(k =>
        `<span class="rp-tag tg-${k}" style="cursor:default">${TG_CN[k]}</span>`).join('')
    + '</div>';
}
async function gcRenderTags(){
  try{
    await ensureTaglib();                    
    const d = TAGLIB;

    const _raw = d.categories || [];
    const cats = (() => {
      if (_raw.some(c => c.subs)) {
        const out = [];
        _raw.forEach(c => (c.subs || []).forEach(s =>
          out.push({ key: s.key || s.label,
                     label: (c.label || '') + ' · ' + (s.label || ''),
                     items: s.items || [] })));
        return out.filter(c => c.items.length);
      }
      return _raw.filter(c => c.key && c.items && c.items.length);
    })();
    $('#gc-tags').innerHTML = gcLegend() + cats.map(c => `<div class="rp-grp"><h4>${esc(c.label||c.key)}</h4>
      <div class="rp-tags">${c.items.slice(0, 400).map(it =>
        `<span class="rp-tag${tgClass(it.en)}"${(it.c ? ` style="background:${it.c};border-color:${it.c}"` : '')} data-en="${esc(it.en)}" title="${esc(tgLabel(it.en) ? ('尺度：'+tgLabel(it.en)+' · ') : '')}${esc(it.cn||'')}">${esc(it.cn||it.en)}</span>`).join('')}</div></div>`).join('');
    $('#gc-tags').querySelectorAll('.rp-tag').forEach(el => {
      if(!el.dataset.en) return;             
      el.onclick = () => {
        const cur = $('#gc-prompt').value.trim();
        $('#gc-prompt').value = (cur ? cur + ', ' : '') + el.dataset.en;
        gcHint();
      };
    });
  }catch(e){ $('#gc-tags').innerHTML = '<div class="rp-grp"><h4>词库加载失败</h4></div>'; }
}

let MYTAGS = [];
async function myTagsLoad(){
  try{
    const d = await post('/api/mytags', {});
    MYTAGS = d.tags || [];
    if(d.cats && !$('#mt-cat').options.length){
      $('#mt-cat').innerHTML = '<option value="custom">未分类</option>'
        + d.cats.map(c => `<option value="${esc(c.key)}">${esc(c.label)}</option>`).join('');
    }
    myTagsRender();
  }catch(e){}
}
function myTagsRender(){
  const box = $('#mt-list'); if(!box) return;
  if(!MYTAGS.length){ box.innerHTML = '<span class="rp-hint">还没有 —— 在下面加一条吧</span>'; return; }
  box.innerHTML = MYTAGS.map(t => {
    const cls = t.tier ? (' tg-' + t.tier) : tgClass(t.en);
    const tip = (t.cn ? t.cn : '') + (t.cat && t.cat !== 'custom' ? (' · ' + t.cat) : '');
    return `<span class="rp-tag mytag${cls}" data-en="${esc(t.en)}" title="${esc(tip)}">${esc(t.cn || t.en)}<span class="del" data-del="${esc(t.en)}">×</span></span>`;
  }).join('');
  box.querySelectorAll('.rp-tag').forEach(el => {
    el.onclick = (ev) => {
      if(ev.target.dataset.del){ myTagDel(ev.target.dataset.del); return; }
      const cur = $('#gc-prompt').value.trim();
      $('#gc-prompt').value = (cur ? cur + ', ' : '') + el.dataset.en;
      gcHint();
    };
  });
  box.querySelectorAll('.del').forEach(el => {
    el.onclick = (ev) => { ev.stopPropagation(); myTagDel(el.dataset.del); };
  });
}
async function myTagSave(){
  const en = $('#mt-en').value.trim();
  if(!en){ alert('英文标签不能为空'); return; }
  const r = await post('/api/mytags/save', {en, cn: $('#mt-cn').value.trim(),
    cat: $('#mt-cat').value || 'custom', tier: $('#mt-tier').value});
  if(r.error){ alert(r.error); return; }
  MYTAGS = r.tags || [];
  $('#mt-en').value = ''; $('#mt-cn').value = '';
  $('#mt-hint').textContent = '已保存 ✓';
  myTagsRender();
}
async function myTagDel(en){
  const r = await post('/api/mytags/del', {en});
  MYTAGS = r.tags || [];
  myTagsRender();
}
async function gachaSubmit(){
  const prompt = gcPromptRaw();
  if(!prompt){ alert('提示词不能为空'); return; }
  const [w, h] = $('#gc-size').value.split('x');
  const body = {prompt, width:+w, height:+h, steps:+$('#gc-steps').value,
                count:+$('#gc-count').value};
  closeGacha();
  toast('🎲 已提交，等出图…');
  const r = await post('/api/gacha', body);
  if(r.error){ alert('提交失败：' + r.error); return; }
  if(r.tier) toast('🎲 已提交 · ' + tierCN(r.tier) + '，等出图…');

  if(r.warnings && r.warnings.length){
    setTimeout(() => toast('⚠️ 自检 ' + r.warnings.length + ' 条：' + r.warnings[0]), 1200);
    console.warn('[ガチャ自检]', r.warnings);
  }
  if(r.position > 0) toast(`⏳ 已排队（前面还有 ${r.position - 1} 个）`);
  pollGacha(r.job);          
}

/* ── StockIQ — Form Interactivity, Calculator, Clock ──────── */

document.addEventListener('DOMContentLoaded', () => {
  // ── Flash message auto-dismiss & click to dismiss ──
  document.querySelectorAll('.flash-msg').forEach(msg => {
    msg.addEventListener('click', () => {
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(30px)';
      setTimeout(() => msg.remove(), 300);
    });
    setTimeout(() => {
      if(document.body.contains(msg)) {
        msg.style.opacity = '0';
        msg.style.transform = 'translateX(30px)';
        setTimeout(() => msg.remove(), 400);
      }
    }, 6000);
  });

  // ── Sidebar toggle (mobile) ──
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (toggle) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      overlay.classList.toggle('open');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('open');
    });
  }

  // ── Live Clock ──
  const clockEl = document.getElementById('liveClock');
  if (clockEl) {
    function updateClock() {
      const now = new Date();
      const days = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
      const months = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'];
      const day = days[now.getDay()];
      const date = now.getDate();
      const month = months[now.getMonth()];
      const year = now.getFullYear();
      const h = String(now.getHours()).padStart(2,'0');
      const m = String(now.getMinutes()).padStart(2,'0');
      const s = String(now.getSeconds()).padStart(2,'0');
      clockEl.innerHTML = `<span class="clock-date">${day}, ${date} ${month} ${year}</span><span class="clock-time">${h}:${m}:${s}</span>`;
    }
    updateClock();
    setInterval(updateClock, 1000);
  }

  // ── Set today's date on all date inputs ──
  document.querySelectorAll('input[type="date"]').forEach(input => {
    if (!input.value) {
      const now = new Date();
      const y = now.getFullYear();
      const m = String(now.getMonth() + 1).padStart(2, '0');
      const d = String(now.getDate()).padStart(2, '0');
      input.value = `${y}-${m}-${d}`;
    }
  });

  // ── Auto-load items & cascading: Bahan → Divisi + Satuan ──
  const mainForm = document.querySelector('form[data-item-type]');
  const bahanSelect = document.getElementById('nama_bahan');
  const divisiInput = document.getElementById('divisi');
  const satuanInput = document.getElementById('satuan');
  const searchInput = document.getElementById('search_bahan');

  let allOptions = []; // Store all options for search filtering

  if (mainForm && bahanSelect) {
    const itemType = mainForm.dataset.itemType || 'bahan';
    const prepareFilter = mainForm.dataset.prepareFilter;

    loadItems(itemType, prepareFilter);

    bahanSelect.addEventListener('change', () => {
      const selected = bahanSelect.options[bahanSelect.selectedIndex];
      if (!selected || !selected.value) {
        if (divisiInput) divisiInput.value = '';
        if (satuanInput) satuanInput.value = '';
        clearField('satuan_prepare');
        clearField('satuan_bahan');
        return;
      }

      if (divisiInput) divisiInput.value = selected.dataset.divisi || '';
      if (satuanInput) satuanInput.value = selected.dataset.satuan || '';

      const satuanPrepareInput = document.getElementById('satuan_prepare');
      const satuanBahanInput = document.getElementById('satuan_bahan');
      if (satuanPrepareInput) satuanPrepareInput.value = selected.dataset.satuanPrepare || '';
      if (satuanBahanInput) satuanBahanInput.value = selected.dataset.satuanBahan || '';
    });

    // ── Search Filter ──
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        const query = searchInput.value.toLowerCase().trim();
        filterBahanOptions(query);
      });
    }
  }

  async function loadItems(itemType, prepareFilter) {
    bahanSelect.innerHTML = '<option value="">Memuat...</option>';

    try {
      let url = `/api/${itemType}`;
      const params = [];
      if (prepareFilter !== undefined && prepareFilter !== null) {
        params.push(`prepare_filter=${prepareFilter}`);
      }
      if (params.length > 0) url += '?' + params.join('&');

      const res = await fetch(url);
      const items = await res.json();

      // Store all items for search
      allOptions = items;

      renderBahanOptions(items);
    } catch (err) {
      bahanSelect.innerHTML = '<option value="">Error memuat data</option>';
    }
  }

  function renderBahanOptions(items) {
    bahanSelect.innerHTML = '<option value="">-- Pilih Bahan --</option>';

    const grouped = {};
    items.forEach(item => {
      const div = item.divisi || 'LAINNYA';
      if (!grouped[div]) grouped[div] = [];
      grouped[div].push(item);
    });

    const sortedDivisi = Object.keys(grouped).sort();
    sortedDivisi.forEach(divisi => {
      const optgroup = document.createElement('optgroup');
      optgroup.label = divisi;

      grouped[divisi].forEach(item => {
        const opt = document.createElement('option');
        opt.value = item.nama_bahan;
        opt.dataset.divisi = item.divisi || '';
        if (item.satuan) opt.dataset.satuan = item.satuan;
        if (item.satuan_npu) opt.dataset.satuan = item.satuan_npu;
        if (item.satuan_prepare) opt.dataset.satuanPrepare = item.satuan_prepare;
        if (item.satuan_bahan) opt.dataset.satuanBahan = item.satuan_bahan;
        opt.textContent = item.nama_bahan;
        optgroup.appendChild(opt);
      });

      bahanSelect.appendChild(optgroup);
    });
  }

  function filterBahanOptions(query) {
    if (!query) {
      renderBahanOptions(allOptions);
      return;
    }
    const filtered = allOptions.filter(item =>
      item.nama_bahan.toLowerCase().includes(query) ||
      (item.divisi && item.divisi.toLowerCase().includes(query))
    );
    renderBahanOptions(filtered);
  }

  function clearField(id) {
    const el = document.getElementById(id);
    if (el) el.value = '';
  }

  // ── Form validation ──
  const forms = document.querySelectorAll('form.validated-form');
  forms.forEach(form => {
    form.addEventListener('submit', (e) => {
      // Skip item validation for kejadian form
      if (form.dataset.noItems === 'true') return;

      const qtyInput = form.querySelector('#qty');
      if (qtyInput && (parseFloat(qtyInput.value) <= 0 || !qtyInput.value)) {
        e.preventDefault();
        alert('Qty harus lebih dari 0');
        qtyInput.focus();
        return;
      }

      const qtyPrepareInput = form.querySelector('#qty_prepare');
      const qtyJadiInput = form.querySelector('#qty_jadi');
      if (qtyPrepareInput && qtyJadiInput) {
        const qtyP = parseFloat(qtyPrepareInput.value) || 0;
        const qtyJ = parseFloat(qtyJadiInput.value) || 0;
        if (qtyP <= 0 && qtyJ <= 0) {
          e.preventDefault();
          alert('Minimal salah satu qty harus diisi');
          qtyPrepareInput.focus();
        }
      }
    });
  });

  // ── Floating Calculator ──
  const calcToggle = document.getElementById('calcToggle');
  const calcWidget = document.getElementById('calculatorWidget');
  const calcClose = document.getElementById('calcClose');

  if (calcToggle && calcWidget) {
    calcToggle.addEventListener('click', () => {
      calcWidget.classList.toggle('open');
      calcToggle.classList.toggle('active');
    });
  }
  if (calcClose) {
    calcClose.addEventListener('click', () => {
      calcWidget.classList.remove('open');
      calcToggle.classList.remove('active');
    });
  }

  // ── Global Confirm Modal for Deletes ──
  const confirmModal = document.getElementById('confirmModal');
  const confirmMessage = document.getElementById('confirmMessage');
  const confirmOk = document.getElementById('confirmOk');
  const confirmCancel = document.getElementById('confirmCancel');
  let currentFormToSubmit = null;

  document.querySelectorAll('form').forEach(form => {
    const onsubmitStr = form.getAttribute('onsubmit');
    if (onsubmitStr && onsubmitStr.includes('confirm(')) {
      // Extract the message
      const match = onsubmitStr.match(/confirm\(['"](.*?)['"]\)/);
      const msg = match ? match[1] : 'Apakah Anda yakin ingin menghapus data ini?';
      
      // Override native confirm
      form.removeAttribute('onsubmit');
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        currentFormToSubmit = form;
        if(confirmMessage) confirmMessage.textContent = msg;
        if(confirmModal) confirmModal.style.display = 'flex';
      });
    }
  });

  if (confirmCancel && confirmModal) {
    confirmCancel.addEventListener('click', () => {
      confirmModal.style.display = 'none';
      currentFormToSubmit = null;
    });
  }

  if (confirmOk && confirmModal) {
    confirmOk.addEventListener('click', () => {
      if (currentFormToSubmit) {
        currentFormToSubmit.submit();
      }
    });
  }
});

// ── Calculator Functions (global scope for onclick) ──
let calcExpression = '';

function calcInput(val) {
  calcExpression += val;
  document.getElementById('calcDisplay').value = calcExpression;
}

function calcClear() {
  calcExpression = '';
  document.getElementById('calcDisplay').value = '';
}

function calcBackspace() {
  calcExpression = calcExpression.slice(0, -1);
  document.getElementById('calcDisplay').value = calcExpression;
}

function calcEval() {
  try {
    const result = Function('"use strict"; return (' + calcExpression + ')')();
    document.getElementById('calcDisplay').value = result;
    calcExpression = String(result);
  } catch {
    document.getElementById('calcDisplay').value = 'Error';
    calcExpression = '';
  }
}

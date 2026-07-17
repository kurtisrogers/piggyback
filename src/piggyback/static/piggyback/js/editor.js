/**
 * Piggyback Card Editor — Fabric.js + Alpine.js
 */
(function () {
  'use strict';

  const canvasEl = document.getElementById('card-canvas');
  if (!canvasEl || typeof fabric === 'undefined') return;

  const editor = document.querySelector('.pb-editor');
  const cardId = editor?.dataset.cardId;

  let textEditCallback = null;

  window.cardEditor = function cardEditor() {
    return {
      title: document.getElementById('card-title')?.value || 'Untitled Card',
      saving: false,
      saveStatus: '',
      saveError: false,
      showSendModal: false,
      editingText: false,
      editTextValue: '',

      openTextEdit(detail) {
        this.editingText = true;
        this.editTextValue = detail.text;
        textEditCallback = detail.onCommit;
        this.$nextTick(() => {
          const overlay = document.querySelector('#text-edit-overlay textarea');
          overlay?.focus();
        });
      },

      commitTextEdit() {
        if (textEditCallback) {
          textEditCallback(this.editTextValue);
          textEditCallback = null;
        }
        this.editingText = false;
      },

      cancelTextEdit() {
        textEditCallback = null;
        this.editingText = false;
      },
    };
  };

  let initialData = {};
  try {
    const raw = document.getElementById('canvas-data')?.textContent || '{}';
    initialData = JSON.parse(raw);
  } catch (e) {
    console.warn('Could not parse canvas data', e);
  }

  const canvas = new fabric.Canvas('card-canvas', {
    backgroundColor: initialData.background || '#FFF8F0',
    selection: true,
    preserveObjectStacking: true,
  });

  if (initialData.objects && initialData.objects.length) {
    initialData.objects.forEach(function (obj) {
      if (obj.type === 'text') {
        const text = new fabric.Text(obj.text || 'Text', {
          left: (obj.left || 100) / 4,
          top: (obj.top || 100) / 4,
          fontSize: (obj.fontSize || 48) / 4,
          fill: obj.fill || '#2D2D2D',
          fontFamily: obj.fontFamily || 'Georgia',
          originX: obj.originX || 'left',
          originY: obj.originY || 'top',
        });
        canvas.add(text);
      }
    });
  }

  document.getElementById('add-text')?.addEventListener('click', function () {
    const fontFamily = document.getElementById('font-family')?.value || 'Georgia';
    const fontSize = parseInt(document.getElementById('font-size')?.value || '48', 10) / 4;
    const fill = document.getElementById('text-color')?.value || '#2D2D2D';

    const text = new fabric.Text('Double-click to edit', {
      left: 100,
      top: 100,
      fontSize: fontSize,
      fill: fill,
      fontFamily: fontFamily,
    });
    canvas.add(text);
    canvas.setActiveObject(text);
  });

  document.getElementById('photo-upload')?.addEventListener('change', function (e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function (ev) {
      fabric.Image.fromURL(ev.target.result, function (img) {
        img.scaleToWidth(150);
        img.set({ left: 80, top: 80 });
        canvas.add(img);
      });
    };
    reader.readAsDataURL(file);
  });

  document.getElementById('sticker-palette')?.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-sticker]');
    if (!btn) return;
    const sticker = new fabric.Text(btn.dataset.sticker, {
      left: 150,
      top: 150,
      fontSize: 48,
    });
    canvas.add(sticker);
  });

  document.getElementById('bg-palette')?.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-color]');
    if (!btn) return;
    canvas.setBackgroundColor(btn.dataset.color, canvas.renderAll.bind(canvas));
  });

  function updateSelected() {
    const obj = canvas.getActiveObject();
    if (!obj || obj.type !== 'text') return;
    const fontFamily = document.getElementById('font-family')?.value;
    const fontSize = parseInt(document.getElementById('font-size')?.value || '48', 10) / 4;
    const fill = document.getElementById('text-color')?.value;
    if (fontFamily) obj.set('fontFamily', fontFamily);
    if (fontSize) obj.set('fontSize', fontSize);
    if (fill) obj.set('fill', fill);
    canvas.renderAll();
  }

  document.getElementById('font-family')?.addEventListener('change', updateSelected);
  document.getElementById('font-size')?.addEventListener('input', updateSelected);
  document.getElementById('text-color')?.addEventListener('input', updateSelected);

  canvas.on('mouse:dblclick', function (opt) {
    const obj = opt.target;
    if (!obj || obj.type !== 'text') return;
    window.dispatchEvent(
      new CustomEvent('pb-edit-text', {
        detail: {
          text: obj.text,
          onCommit: function (updated) {
            obj.set('text', updated);
            canvas.renderAll();
          },
        },
      })
    );
  });

  function getCanvasData() {
    const objects = canvas.getObjects().map(function (obj) {
      if (obj.type === 'text') {
        return {
          type: 'text',
          text: obj.text,
          left: obj.left * 4,
          top: obj.top * 4,
          fontSize: obj.fontSize * 4,
          fill: obj.fill,
          fontFamily: obj.fontFamily,
          originX: obj.originX,
          originY: obj.originY,
        };
      }
      if (obj.type === 'image') {
        return {
          type: 'image',
          left: obj.left * 4,
          top: obj.top * 4,
          scaleX: obj.scaleX,
          scaleY: obj.scaleY,
          src: obj.getSrc ? obj.getSrc() : '',
        };
      }
      return null;
    }).filter(Boolean);

    return {
      version: '5.3.0',
      background: canvas.backgroundColor,
      objects: objects,
    };
  }

  function getEditorAlpine() {
    if (!editor || !editor._x_dataStack) return null;
    return editor._x_dataStack[0];
  }

  function showToast(message, type) {
    window.dispatchEvent(new CustomEvent('pb-toast', { detail: { message: message, type: type || 'success' } }));
  }

  document.getElementById('save-card')?.addEventListener('click', async function () {
    if (!cardId) {
      showToast('Please sign in to save your card.', 'error');
      return;
    }

    const alpine = getEditorAlpine();
    if (alpine) {
      alpine.saving = true;
      alpine.saveStatus = '';
      alpine.saveError = false;
    }

    const payload = {
      canvas_data: getCanvasData(),
      inside_message: document.getElementById('inside-message')?.value || '',
      title: alpine?.title || document.getElementById('card-title')?.value || 'Untitled Card',
    };

    try {
      const resp = await fetch('/api/cards/' + cardId + '/save_design/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(payload),
      });
      if (resp.ok) {
        showToast('Card saved!');
        if (alpine) alpine.saveStatus = 'Saved';
      } else {
        showToast('Save failed. Are you signed in?', 'error');
        if (alpine) {
          alpine.saveStatus = 'Save failed';
          alpine.saveError = true;
        }
      }
    } catch (err) {
      console.error(err);
      showToast('Save failed.', 'error');
      if (alpine) {
        alpine.saveStatus = 'Save failed';
        alpine.saveError = true;
      }
    } finally {
      if (alpine) alpine.saving = false;
    }
  });

  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : '';
  }
})();

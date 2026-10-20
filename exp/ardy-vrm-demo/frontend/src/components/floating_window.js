/**
 * Floating, Draggable, and Resizable Tool Window Component.
 * Supports dragging by header, resizing via handle, collapsing, opacity adjustment,
 * and z-index elevation while preventing pointer events from bleeding into OrbitControls.
 */

export class FloatingWindow {
  /**
   * @param {HTMLElement} element - The window container element (.floating-window)
   * @param {object} options
   * @param {string} [options.title] - Window title
   * @param {number} [options.minWidth] - Minimum width in pixels
   * @param {number} [options.minHeight] - Minimum height in pixels
   * @param {number} [options.initialX] - Initial left in pixels
   * @param {number} [options.initialY] - Initial top in pixels
   * @param {Function} [options.onClose] - Callback when closed
   */
  constructor(element, options = {}) {
    this.el = element;
    this.minWidth = options.minWidth || 280;
    this.minHeight = options.minHeight || 160;
    this.onClose = options.onClose || null;

    this.header = this.el.querySelector('.window-header');
    this.body = this.el.querySelector('.window-body');
    this.resizeHandle = this.el.querySelector('.window-resize-handle');
    this.btnCollapse = this.el.querySelector('.btn-window-collapse');
    this.btnClose = this.el.querySelector('.btn-window-close');
    this.opacitySlider = this.el.querySelector('.window-opacity-slider');

    this.isDragging = false;
    this.isResizing = false;
    this.isCollapsed = false;
    this.isVisible = true;

    this.dragStart = { x: 0, y: 0 };
    this.windowStart = { x: 0, y: 0, width: 0, height: 0 };

    this.init(options);
  }

  init(options) {
    // Set initial position if specified
    if (options.initialX !== undefined) {
      this.el.style.left = `${options.initialX}px`;
    }
    if (options.initialY !== undefined) {
      this.el.style.top = `${options.initialY}px`;
    }

    // Isolate all window pointer events from canvas OrbitControls
    this.el.addEventListener('pointerdown', (e) => {
      e.stopPropagation();
      this.bringToFront();
    });

    // Setup Header Dragging
    if (this.header) {
      this.header.addEventListener('pointerdown', (e) => this.onDragStart(e));
    }

    // Setup Resize Handle
    if (this.resizeHandle) {
      this.resizeHandle.addEventListener('pointerdown', (e) => this.onResizeStart(e));
    }

    // Setup Collapse Toggle
    if (this.btnCollapse) {
      this.btnCollapse.addEventListener('click', (e) => {
        e.stopPropagation();
        this.toggleCollapse();
      });
    }

    // Setup Close Button
    if (this.btnClose) {
      this.btnClose.addEventListener('click', (e) => {
        e.stopPropagation();
        this.hide();
        if (this.onClose) this.onClose();
      });
    }

    // Setup Opacity Slider
    if (this.opacitySlider) {
      this.opacitySlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        this.setOpacity(val);
      });
    }

    // Global pointer move and up handlers
    window.addEventListener('pointermove', (e) => {
      if (this.isDragging) this.onDragMove(e);
      if (this.isResizing) this.onResizeMove(e);
    });

    window.addEventListener('pointerup', () => {
      if (this.isDragging) this.onDragEnd();
      if (this.isResizing) this.onResizeEnd();
    });
  }

  bringToFront() {
    FloatingWindow.highestZIndex = (FloatingWindow.highestZIndex || 100) + 1;
    this.el.style.zIndex = FloatingWindow.highestZIndex;
  }

  onDragStart(e) {
    if (e.target.closest('button') || e.target.closest('input')) return;
    this.isDragging = true;
    this.dragStart.x = e.clientX;
    this.dragStart.y = e.clientY;

    const rect = this.el.getBoundingClientRect();
    this.windowStart.x = rect.left;
    this.windowStart.y = rect.top;

    this.header.classList.add('is-dragging');
    e.preventDefault();
  }

  onDragMove(e) {
    if (!this.isDragging) return;
    const dx = e.clientX - this.dragStart.x;
    const dy = e.clientY - this.dragStart.y;

    const newX = this.windowStart.x + dx;
    const newY = this.windowStart.y + dy;

    // Viewport clamping
    const maxLeft = Math.max(0, window.innerWidth - this.el.offsetWidth);
    const maxTop = Math.max(48, window.innerHeight - 44);

    const clampedX = Math.max(0, Math.min(newX, maxLeft));
    const clampedY = Math.max(48, Math.min(newY, maxTop));

    this.el.style.left = `${clampedX}px`;
    this.el.style.top = `${clampedY}px`;
    this.el.style.right = 'auto';
    this.el.style.bottom = 'auto';
  }

  onDragEnd() {
    this.isDragging = false;
    this.header.classList.remove('is-dragging');
  }

  onResizeStart(e) {
    this.isResizing = true;
    this.dragStart.x = e.clientX;
    this.dragStart.y = e.clientY;

    const rect = this.el.getBoundingClientRect();
    this.windowStart.width = rect.width;
    this.windowStart.height = rect.height;

    this.el.classList.add('is-resizing');
    e.preventDefault();
  }

  onResizeMove(e) {
    if (!this.isResizing) return;
    const dx = e.clientX - this.dragStart.x;
    const dy = e.clientY - this.dragStart.y;

    const newWidth = Math.max(this.minWidth, Math.min(this.windowStart.width + dx, window.innerWidth - 20));
    const newHeight = Math.max(this.minHeight, Math.min(this.windowStart.height + dy, window.innerHeight - 60));

    this.el.style.width = `${newWidth}px`;
    if (!this.isCollapsed) {
      this.el.style.height = `${newHeight}px`;
    }
  }

  onResizeEnd() {
    this.isResizing = false;
    this.el.classList.remove('is-resizing');
  }

  toggleCollapse() {
    this.isCollapsed = !this.isCollapsed;
    this.el.classList.toggle('is-collapsed', this.isCollapsed);
    if (this.btnCollapse) {
      this.btnCollapse.title = this.isCollapsed ? 'Expand window' : 'Collapse window';
      this.btnCollapse.innerHTML = this.isCollapsed
        ? '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>'
        : '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"/></svg>';
    }
  }

  setOpacity(val) {
    const clamped = Math.max(0.35, Math.min(1.0, val));
    this.el.style.backgroundColor = `rgba(15, 23, 42, ${clamped})`;
  }

  show() {
    this.isVisible = true;
    this.el.classList.remove('is-hidden');
    this.bringToFront();
  }

  hide() {
    this.isVisible = false;
    this.el.classList.add('is-hidden');
  }

  toggle() {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
    return this.isVisible;
  }
}

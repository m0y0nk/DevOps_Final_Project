import React, { useState, useEffect } from 'react';

export default function App() {
  const [activeTab, setActiveTab] = useState('inventory');
  const [items, setItems] = useState([]);
  const [checkouts, setCheckouts] = useState([]);
  const [activities, setActivities] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [conditionFilter, setConditionFilter] = useState('');

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  // Form states
  const [newItem, setNewItem] = useState({
    name: '',
    sku: '',
    description: '',
    category: 'Electronics',
    quantity_total: 1,
    quantity_available: 1,
    low_stock_threshold: 1,
    condition: 'good',
    location: '',
  });

  const [checkoutData, setCheckoutData] = useState({
    borrower_name: '',
    borrower_contact: '',
    quantity: 1,
    due_days: 7,
  });

  // Fetch Dashboard Stats
  const fetchStats = async () => {
    try {
      const res = await fetch('/api/dashboard/stats');
      if (!res.ok) throw new Error('Failed to load stats');
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error(err);
    }
  };

  // Fetch Items
  const fetchItems = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = '/api/items?';
      if (search) url += `search=${encodeURIComponent(search)}&`;
      if (categoryFilter) url += `category=${encodeURIComponent(categoryFilter)}&`;
      if (conditionFilter) url += `condition=${encodeURIComponent(conditionFilter)}&`;

      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch items');
      const data = await res.json();
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch Checkouts
  const fetchCheckouts = async () => {
    try {
      const res = await fetch('/api/checkouts');
      if (res.ok) {
        const data = await res.json();
        setCheckouts(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Fetch Activities
  const fetchActivities = async () => {
    try {
      const res = await fetch('/api/activity');
      if (res.ok) {
        const data = await res.json();
        setActivities(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const refreshAll = () => {
    fetchStats();
    fetchItems();
    fetchCheckouts();
    fetchActivities();
  };

  useEffect(() => {
    refreshAll();
  }, [search, categoryFilter, conditionFilter]);

  // Create Item Handler
  const handleCreateItem = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...newItem,
        quantity_total: parseInt(newItem.quantity_total, 10),
        quantity_available: parseInt(newItem.quantity_total, 10),
        low_stock_threshold: parseInt(newItem.low_stock_threshold, 10),
      };
      const res = await fetch('/api/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Could not create item');
      }
      setShowCreateModal(false);
      setNewItem({
        name: '',
        sku: '',
        description: '',
        category: 'Electronics',
        quantity_total: 1,
        quantity_available: 1,
        low_stock_threshold: 1,
        condition: 'good',
        location: '',
      });
      refreshAll();
    } catch (err) {
      alert(`Error creating item: ${err.message}`);
    }
  };

  // Delete Item Handler
  const handleDeleteItem = async (item) => {
    if (!window.confirm(`Are you sure you want to delete "${item.name}"?`)) return;
    try {
      const res = await fetch(`/api/items/${item.id}`, { method: 'DELETE' });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to delete item');
      }
      refreshAll();
    } catch (err) {
      alert(err.message);
    }
  };

  // Checkout Handler
  const handleCheckoutSubmit = async (e) => {
    e.preventDefault();
    if (!selectedItem) return;

    try {
      const dueDate = new Date();
      dueDate.setDate(dueDate.getDate() + parseInt(checkoutData.due_days, 10));

      const payload = {
        borrower_name: checkoutData.borrower_name,
        borrower_contact: checkoutData.borrower_contact,
        quantity: parseInt(checkoutData.quantity, 10),
        due_at: dueDate.toISOString(),
      };

      const res = await fetch(`/api/items/${selectedItem.id}/checkouts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Checkout failed');
      }

      setShowCheckoutModal(false);
      setCheckoutData({ borrower_name: '', borrower_contact: '', quantity: 1, due_days: 7 });
      refreshAll();
    } catch (err) {
      alert(`Checkout failed: ${err.message}`);
    }
  };

  // Return Handler
  const handleReturnCheckout = async (checkoutId) => {
    try {
      const res = await fetch(`/api/checkouts/${checkoutId}/return`, {
        method: 'POST',
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Return failed');
      }
      refreshAll();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">🔬</span>
          <div>
            <div className="brand-name">LabTrack</div>
            <div className="brand-tag">v1.0 • Capstone</div>
          </div>
        </div>

        <ul className="nav-links">
          <li
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </li>
          <li
            className={`nav-item ${activeTab === 'inventory' ? 'active' : ''}`}
            onClick={() => setActiveTab('inventory')}
          >
            📦 Equipment & Items
          </li>
          <li
            className={`nav-item ${activeTab === 'checkouts' ? 'active' : ''}`}
            onClick={() => setActiveTab('checkouts')}
          >
            📋 Checkouts ({checkouts.filter((c) => c.status === 'checked_out').length})
          </li>
          <li
            className={`nav-item ${activeTab === 'activity' ? 'active' : ''}`}
            onClick={() => setActiveTab('activity')}
          >
            ⚡ Activity Feed
          </li>
        </ul>

        <div className="sidebar-footer">
          <div className="status-indicator">
            <span className="status-dot"></span>
            <span>API Online • PostgreSQL</span>
          </div>
          <div>University Makerspace Hub</div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <header className="top-bar">
          <div className="page-title">
            {activeTab === 'dashboard' && 'Dashboard Overview'}
            {activeTab === 'inventory' && 'Lab Equipment & Inventory'}
            {activeTab === 'checkouts' && 'Equipment Checkout Records'}
            {activeTab === 'activity' && 'Real-time Activity Log'}
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="btn-secondary" onClick={refreshAll}>
              🔄 Refresh
            </button>
            <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
              + New Item
            </button>
          </div>
        </header>

        <div className="content-area">
          {error && (
            <div className="error-banner">
              <span>{error}</span>
              <button className="modal-close" onClick={() => setError(null)}>×</button>
            </div>
          )}

          {/* KPI Stat Cards (Shown on Dashboard & Inventory) */}
          {stats && (
            <div className="kpi-grid">
              <div className="kpi-card">
                <span className="kpi-label">Distinct Items</span>
                <span className="kpi-value">{stats.total_distinct_items}</span>
                <span className="kpi-sub">Unique models/SKUs</span>
              </div>
              <div className="kpi-card">
                <span className="kpi-label">Units Available / Owned</span>
                <span className="kpi-value">{stats.total_units_available} <span style={{fontSize: '16px', color: '#94a3b8'}}>/ {stats.total_units_owned}</span></span>
                <span className="kpi-sub">{Math.round((stats.total_units_available / (stats.total_units_owned || 1)) * 100)}% available</span>
              </div>
              <div className="kpi-card">
                <span className="kpi-label">Active Borrowers</span>
                <span className="kpi-value">{stats.active_checkouts_count}</span>
                <span className="kpi-sub">Items currently checked out</span>
              </div>
              <div className="kpi-card kpi-warn">
                <span className="kpi-label">Low Stock Warnings</span>
                <span className="kpi-value">{stats.low_stock_items_count}</span>
                <span className="kpi-sub">≤ threshold units</span>
              </div>
              <div className="kpi-card kpi-alert">
                <span className="kpi-label">Needs Maintenance</span>
                <span className="kpi-value">{stats.items_needing_repair_count}</span>
                <span className="kpi-sub">Requires repair or service</span>
              </div>
            </div>
          )}

          {/* TAB 1: INVENTORY TABLE */}
          {activeTab === 'inventory' && (
            <div>
              <div className="filter-bar">
                <input
                  type="text"
                  className="search-input"
                  placeholder="🔍 Search items by name, SKU, or description..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
                <select
                  className="select-input"
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <option value="">All Categories</option>
                  <option value="Electronics">Electronics</option>
                  <option value="Tools">Tools</option>
                  <option value="Optics">Optics</option>
                  <option value="Power Supplies">Power Supplies</option>
                  <option value="Rapid Prototyping">Rapid Prototyping</option>
                  <option value="Test & Measurement">Test & Measurement</option>
                  <option value="Digital Tools">Digital Tools</option>
                </select>
                <select
                  className="select-input"
                  value={conditionFilter}
                  onChange={(e) => setConditionFilter(e.target.value)}
                >
                  <option value="">All Conditions</option>
                  <option value="good">Good Condition</option>
                  <option value="needs_repair">Needs Repair</option>
                  <option value="retired">Retired</option>
                </select>
              </div>

              <div className="table-card">
                {loading ? (
                  <div className="state-box">Loading inventory items...</div>
                ) : items.length === 0 ? (
                  <div className="state-box">No items match your filter criteria.</div>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th>Item & SKU</th>
                        <th>Category</th>
                        <th>Available / Total</th>
                        <th>Condition</th>
                        <th>Location</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {items.map((item) => (
                        <tr key={item.id}>
                          <td>
                            <div style={{ fontWeight: 600, color: '#fff' }}>{item.name}</div>
                            <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                              SKU: {item.sku}
                              {item.is_low_stock && (
                                <span className="low-stock-tag">⚠️ Low Stock</span>
                              )}
                            </div>
                          </td>
                          <td>{item.category}</td>
                          <td>
                            <span style={{ fontWeight: 600, color: item.quantity_available === 0 ? '#ef4444' : '#10b981' }}>
                              {item.quantity_available}
                            </span>{' '}
                            / {item.quantity_total}
                          </td>
                          <td>
                            <span
                              className={`badge ${
                                item.condition === 'good'
                                  ? 'badge-good'
                                  : item.condition === 'needs_repair'
                                  ? 'badge-repair'
                                  : 'badge-retired'
                              }`}
                            >
                              {item.condition.replace('_', ' ')}
                            </span>
                          </td>
                          <td>{item.location || '—'}</td>
                          <td>
                            <div style={{ display: 'flex', gap: '8px' }}>
                              <button
                                className="btn-action"
                                disabled={item.quantity_available === 0}
                                style={{ opacity: item.quantity_available === 0 ? 0.4 : 1 }}
                                onClick={() => {
                                  setSelectedItem(item);
                                  setShowCheckoutModal(true);
                                }}
                              >
                                Checkout
                              </button>
                              <button
                                className="btn-danger"
                                onClick={() => handleDeleteItem(item)}
                              >
                                Delete
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: CHECKOUTS TABLE */}
          {activeTab === 'checkouts' && (
            <div className="table-card">
              <table>
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Borrower</th>
                    <th>Quantity</th>
                    <th>Date Borrowed</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {checkouts.length === 0 ? (
                    <tr>
                      <td colSpan="6" style={{ textAlign: 'center', padding: '32px' }}>
                        No checkout records found.
                      </td>
                    </tr>
                  ) : (
                    checkouts.map((co) => (
                      <tr key={co.id}>
                        <td style={{ fontWeight: 600, color: '#fff' }}>
                          {co.item_name || `Item #${co.item_id}`}
                        </td>
                        <td>
                          <div>{co.borrower_name}</div>
                          <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                            {co.borrower_contact || 'No contact provided'}
                          </div>
                        </td>
                        <td>{co.quantity}</td>
                        <td>{new Date(co.checked_out_at).toLocaleDateString()}</td>
                        <td>
                          <span
                            className={`badge ${
                              co.status === 'checked_out'
                                ? 'badge-checked-out'
                                : 'badge-returned'
                            }`}
                          >
                            {co.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td>
                          {co.status === 'checked_out' ? (
                            <button
                              className="btn-action"
                              onClick={() => handleReturnCheckout(co.id)}
                            >
                              Record Return
                            </button>
                          ) : (
                            <span style={{ fontSize: '12px', color: '#64748b' }}>Returned</span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 3: ACTIVITY FEED */}
          {activeTab === 'activity' && (
            <div className="activity-list">
              {activities.length === 0 ? (
                <div className="state-box">No activity events recorded yet.</div>
              ) : (
                activities.map((act) => (
                  <div key={act.id} className="activity-item">
                    <div>
                      <div className="activity-summary">{act.summary}</div>
                      <div style={{ fontSize: '11px', color: '#06b6d4', marginTop: '4px' }}>
                        Event: {act.event_type}
                      </div>
                    </div>
                    <div className="activity-time">
                      {new Date(act.created_at).toLocaleString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* TAB 4: DASHBOARD HOME */}
          {activeTab === 'dashboard' && (
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
              <div>
                <h3 style={{ marginBottom: '16px', color: '#fff' }}>Recent Activity</h3>
                <div className="activity-list">
                  {activities.slice(0, 5).map((act) => (
                    <div key={act.id} className="activity-item">
                      <div className="activity-summary">{act.summary}</div>
                      <div className="activity-time">
                        {new Date(act.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 style={{ marginBottom: '16px', color: '#fff' }}>Quick Actions</h3>
                <div style={{ background: '#1e293b', padding: '20px', borderRadius: '10px', border: '1px solid #334155', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <button className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={() => setShowCreateModal(true)}>
                    + Add New Inventory Item
                  </button>
                  <button className="btn-secondary" style={{ width: '100%' }} onClick={() => setActiveTab('inventory')}>
                    📦 Browse Full Equipment Catalog
                  </button>
                  <button className="btn-secondary" style={{ width: '100%' }} onClick={() => setActiveTab('checkouts')}>
                    📋 View Active Loans
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* CREATE ITEM MODAL */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">Create New Inventory Item</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreateItem}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Item Name *</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    value={newItem.name}
                    onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                    placeholder="e.g. Rigol Digital Oscilloscope 100MHz"
                  />
                </div>
                <div className="form-group">
                  <label>SKU (Stock Keeping Unit) *</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    value={newItem.sku}
                    onChange={(e) => setNewItem({ ...newItem, sku: e.target.value })}
                    placeholder="e.g. OSC-1054Z-01"
                  />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="form-group">
                    <label>Category</label>
                    <input
                      type="text"
                      className="form-input"
                      value={newItem.category}
                      onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Total Quantity</label>
                    <input
                      type="number"
                      min="1"
                      className="form-input"
                      value={newItem.quantity_total}
                      onChange={(e) => setNewItem({ ...newItem, quantity_total: e.target.value })}
                    />
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="form-group">
                    <label>Low Stock Alert Level</label>
                    <input
                      type="number"
                      min="0"
                      className="form-input"
                      value={newItem.low_stock_threshold}
                      onChange={(e) => setNewItem({ ...newItem, low_stock_threshold: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Location / Bench</label>
                    <input
                      type="text"
                      className="form-input"
                      value={newItem.location}
                      onChange={(e) => setNewItem({ ...newItem, location: e.target.value })}
                      placeholder="e.g. Shelf B2"
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    rows="2"
                    className="form-input"
                    value={newItem.description}
                    onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                    placeholder="Detailed specifications, probe models, serial numbers..."
                  ></textarea>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Item
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CHECKOUT MODAL */}
      {showCheckoutModal && selectedItem && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">Checkout: {selectedItem.name}</h2>
              <button className="modal-close" onClick={() => setShowCheckoutModal(false)}>×</button>
            </div>
            <form onSubmit={handleCheckoutSubmit}>
              <div className="modal-body">
                <div style={{ background: '#0f172a', padding: '12px', borderRadius: '6px', fontSize: '13px' }}>
                  <div><strong>Available Units:</strong> {selectedItem.quantity_available} of {selectedItem.quantity_total}</div>
                  <div><strong>Location:</strong> {selectedItem.location || 'Not specified'}</div>
                </div>
                <div className="form-group">
                  <label>Borrower Full Name *</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    value={checkoutData.borrower_name}
                    onChange={(e) => setCheckoutData({ ...checkoutData, borrower_name: e.target.value })}
                    placeholder="e.g. Dr. Alex Morgan"
                  />
                </div>
                <div className="form-group">
                  <label>Borrower Email / Contact</label>
                  <input
                    type="text"
                    className="form-input"
                    value={checkoutData.borrower_contact}
                    onChange={(e) => setCheckoutData({ ...checkoutData, borrower_contact: e.target.value })}
                    placeholder="alex.m@university.edu"
                  />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="form-group">
                    <label>Quantity to Borrow</label>
                    <input
                      type="number"
                      min="1"
                      max={selectedItem.quantity_available}
                      required
                      className="form-input"
                      value={checkoutData.quantity}
                      onChange={(e) => setCheckoutData({ ...checkoutData, quantity: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>Loan Duration (Days)</label>
                    <input
                      type="number"
                      min="1"
                      max="30"
                      className="form-input"
                      value={checkoutData.due_days}
                      onChange={(e) => setCheckoutData({ ...checkoutData, due_days: e.target.value })}
                    />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowCheckoutModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Confirm Checkout
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

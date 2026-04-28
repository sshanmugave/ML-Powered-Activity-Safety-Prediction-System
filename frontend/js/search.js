/**
 * SafeTravel - Place Search (Nominatim/OpenStreetMap)
 */

const Search = {
  selectedPlace: null,
  
  /**
   * Search for places using Nominatim
   */
  async searchPlaces(query) {
    if (!query || query.length < 3) return [];
    
    try {
      const url = `https://nominatim.openstreetmap.org/search?` +
        `q=${encodeURIComponent(query)}&format=json&limit=6&addressdetails=1&extratags=1`;
      
      const res = await fetch(url, {
        headers: { 'User-Agent': 'SafeTravel/1.0' }
      });
      
      if (!res.ok) return [];
      
      const results = await res.json();
      
      return results.map(r => ({
        name: r.display_name.split(',')[0],
        fullName: r.display_name,
        lat: parseFloat(r.lat),
        lon: parseFloat(r.lon),
        type: r.type || r.class || 'place',
        osmType: r.class,
        address: r.address || {},
        placeType: Search.detectPlaceType(r)
      }));
    } catch (e) {
      console.error('Search error:', e);
      return [];
    }
  },

  /**
   * Detect place type from Nominatim result
   */
  detectPlaceType(result) {
    const type = (result.type || '').toLowerCase();
    const cls = (result.class || '').toLowerCase();
    const name = (result.display_name || '').toLowerCase();
    
    // Map Nominatim types to our place types
    if (['park', 'recreation_ground', 'playground', 'dog_park'].includes(type)) return 'park';
    if (['water', 'lake', 'reservoir', 'pond'].includes(type) || name.includes('lake')) return 'lake';
    if (['temple', 'place_of_worship', 'church', 'mosque', 'synagogue'].includes(type) ||
        name.includes('temple') || name.includes('mandir') || name.includes('masjid') ||
        name.includes('church') || name.includes('gurudwara')) return 'temple';
    if (['marketplace', 'market', 'bazaar'].includes(type) || 
        name.includes('market') || name.includes('bazaar')) return 'market';
    if (['beach'].includes(type) || name.includes('beach')) return 'beach';
    if (['peak', 'hill', 'mountain', 'ridge'].includes(type) ||
        name.includes('hill') || name.includes('mountain')) return 'hill';
    if (['monument', 'memorial', 'castle', 'fort', 'ruins', 'archaeological_site'].includes(type) ||
        name.includes('fort') || name.includes('monument') || name.includes('tomb') ||
        name.includes('mahal') || name.includes('qutub') || name.includes('heritage')) return 'monument';
    if (['mall', 'department_store', 'shopping'].includes(type) ||
        name.includes('mall') || name.includes('shopping')) return 'mall';
    if (['garden', 'botanical'].includes(type) || name.includes('garden') || name.includes('bagh')) return 'garden';
    if (['river', 'riverbank', 'stream'].includes(type) || 
        name.includes('ghat') || name.includes('river')) return 'riverside';
    if (['zoo', 'wildlife_park', 'nature_reserve'].includes(type) || name.includes('zoo')) return 'zoo';
    if (['stadium', 'sports_centre', 'pitch'].includes(type) || name.includes('stadium')) return 'stadium';
    
    return 'other';
  },

  /**
   * Render search results dropdown
   */
  renderResults(results, container) {
    if (results.length === 0) {
      container.innerHTML = '<div class="search-result-item"><span class="place-name">No results found</span></div>';
      show(container);
      return;
    }

    container.innerHTML = results.map((r, i) => `
      <div class="search-result-item" data-index="${i}">
        <span style="font-size:1.2rem">${Search.getPlaceEmoji(r.placeType)}</span>
        <div>
          <div class="place-name">${r.name}</div>
          <div class="place-detail">${r.fullName.substring(0, 80)}${r.fullName.length > 80 ? '...' : ''}</div>
        </div>
      </div>
    `).join('');

    show(container);

    // Attach click handlers
    container.querySelectorAll('.search-result-item').forEach(item => {
      item.addEventListener('click', () => {
        const idx = parseInt(item.dataset.index);
        Search.selectPlace(results[idx]);
      });
    });
  },

  /**
   * Select a place from results
   */
  selectPlace(place) {
    Search.selectedPlace = place;
    
    const input = $('#place-input');
    input.value = place.name;
    
    // Update place type dropdown
    const typeSelect = $('#place-type-select');
    typeSelect.value = place.placeType;
    
    // Show selected info
    const info = $('#selected-place-info');
    info.textContent = `📍 ${place.fullName.substring(0, 100)} (${place.lat.toFixed(4)}, ${place.lon.toFixed(4)})`;
    show(info);
    
    // Hide results
    hide('#search-results');
    
    // Enable predict button
    $('#btn-predict').disabled = false;
    
    showToast(`Selected: ${place.name}`, 'success', 2000);
  },

  /**
   * Get emoji for place type
   */
  getPlaceEmoji(type) {
    const emojis = {
      park: '🌳', lake: '🏞️', temple: '🛕', market: '🏪', beach: '🏖️',
      hill: '⛰️', monument: '🏛️', mall: '🏬', garden: '🌺', riverside: '🌊',
      zoo: '🦁', stadium: '🏟️', other: '📍'
    };
    return emojis[type] || '📍';
  }
};

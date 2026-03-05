import { browser } from '$app/environment';
import { writable } from "svelte/store";

// Svelte Store
export const view = writable(null);

// fav() tagastab API konkreetse localStorage KEY jaoks
export function fav(KEY = "save:local"){

  // Loeb andmed localStorage-st
  function read(){
    if (!browser) return {};
    try { 
      const val = JSON.parse(localStorage.getItem(KEY));
      // Kui localStorage väärtus ei ole objekt → tagasta tühjaks objektiks
      if (!val || typeof val !== 'object') return {};
      return val;
    }
    catch { return {}; } 
  }

  // Salvestab andmed localStorage-sse ja uuendab store
  function write(data){
    if (!browser) return;
    localStorage.setItem(KEY, JSON.stringify(data));
    view.set(data); 
  }

  return {

    // Tagastab kogu salvestatud andmestiku
    get: () => {
      const data = read();
      view.set(data); // sync UI-ga
      return data; 
    },

    // Lisab või eemaldab ID (toggle)
    save: (what, id) => {
      const data = read();

      // Veendu, et kategooria on array
      if (!Array.isArray(data[what])) data[what] = [];

      const index = data[what].indexOf(id);
      if (index !== -1) { data[what].splice(index, 1); } 
      else { data[what].push(id); }

      // Kui kategooria jäi tühjaks → kustuta
      if (data[what].length === 0) { delete data[what]; }

      write(data);
    },

    // Asendab kategooria täielikult uue ID listiga
    replace: (what, json = []) => {
      const data = read();
      
      // turvalisus: veendu, et json on array
      if (!Array.isArray(json)) json = [];

      if (json.length === 0) { delete data[what]; } 
      else { data[what] = [...json]; }

      write(data);
    },

    // Eemaldab konkreetse ID
    remove: (what, id) => {
      const data = read();

      // Kui kategooria ei ole array → pole midagi teha
      if (!Array.isArray(data[what])) return;

      const index = data[what].indexOf(id);
      if (index !== -1) { data[what].splice(index, 1); }

      if (data[what].length === 0) { delete data[what]; }

      write(data);
    },

    // Kustutab terve kategooria (nt movie või tv)
    delete: (what) => {
      const data = read();
      console.log(what + " deleted");
      delete data[what];
      write(data);
    },

    // Kustutab KÕIK saved andmed
    delete_all: () => {
      if (!browser) return;
      console.log("🟡", "All your saved local data deleted");
      localStorage.removeItem(KEY);
      view.set(null);
    }

  }
}
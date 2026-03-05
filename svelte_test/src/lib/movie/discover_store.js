import { browser } from '$app/environment';
import { writable } from "svelte/store";

// Svelte Store
export const view = writable(null);

// Data Management (LocalStorage)
export function save(slug, what, id) {

  /*
    load $view -> (layout.svelte)

    slug: name where data saved
    what: save / get / delete
    id: data identifier in slug array (used only when what is 'save')
  */

  let array = { [slug]: [] };

  if (browser) {
    if (what == 'get'){ let back
      try { back = JSON.parse(localStorage.getItem("save:discover"))[slug] } 
      catch { return null } 
      finally { return back }
    }

    // Create if none
    if (what) {
      if (!localStorage.getItem("save:discover")) {
        localStorage.setItem('save:discover', JSON.stringify(array));
      }
    }

    // Get categories & items
    let save_list = JSON.parse(localStorage.getItem("save:discover"));
    let save_sub = save_list[slug];

    if(what === 'delete_all'){
      console.log("All your saved local data deleted")
      localStorage.removeItem('save:discover');
      view.set()
      return
    }
    if(what== 'remove'){
      if (save_sub.includes(id)) save_sub.splice(save_sub.indexOf(id), 1)
    }
  
    // Handle 'save' case
    if (what === 'save') {
      if (!save_sub) {
        save_list[slug] = [];
        save_sub = save_list[slug] }

      if (save_sub.includes(id)) save_sub.splice(save_sub.indexOf(id), 1) 
      else save_sub.push(id) 
    } 

    // Remove empty category
    if (save_sub.length === 0) {
        delete save_list[slug]; }

  // Handle 'delete' case
    if (what === 'delete') {
      console.log(slug +" deleted")
      delete save_list[slug] }

  // Update localStorage
    localStorage.setItem('save:discover', JSON.stringify(save_list));

    // Update the Svelte store
    view.set(save_list);
  }
}
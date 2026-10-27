import {lstat} from 'node:fs/promises';
import {join} from 'node:path';
export const MIGRATION_MARKER='.migration-in-progress';
export async function assertMigrationComplete(directory){
 try{await lstat(join(directory,MIGRATION_MARKER));}catch(error){if(error.code==='ENOENT')return;throw Error('Migration status could not be read.');}
 throw Error('The camera configuration migration is incomplete. Verify or restore the saved data before starting.');
}


## Minu andmed
### kirjutamine
```
import fs from 'fs/promises';

await fs.writeFile('/data/movies.json', JSON.stringify({ test: 123 }));
```
### lugemine
```
import fs from 'fs/promises';

const data = await fs.readFile('/data/movies.json', 'utf8');
console.log(JSON.parse(data));
```
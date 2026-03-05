## Päri seadmeid

### Kõik
```
const res = await fetch("http://supervisor/core/api/states", {
	headers: {
		Authorization: `Bearer ${process.env.SUPERVISOR_TOKEN}`
	}
});

const devices = await res.json();
```

### Üks
```
const res = await fetch("http://supervisor/core/api/states/sensor.temperature", {
	headers: {
		Authorization: `Bearer ${process.env.SUPERVISOR_TOKEN}`,
		"Content-Type": "application/json"
	}
});

const data = await res.json();
console.log(data.state);
```






## Muud mountitud kaustad
/data	- addoni püsiv storage
/config	- Home Assistanti config kaust
/media	- media kaust
/ssl	- sertifikaadid
```
await fs.readFile('/config/configuration.yaml')
```



## DO
```
await fetch("http://supervisor/core/api/services/light/toggle", {
	method: "POST",
	headers: {
		Authorization: `Bearer ${process.env.SUPERVISOR_TOKEN}`,
		"Content-Type": "application/json"
	},
	body: JSON.stringify({
		entity_id: "light.living_room"
	})
});
```
`turn_on`, `turn_off`
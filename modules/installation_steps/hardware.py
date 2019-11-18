import json
from os.path import isdir, isfile

html = """
<div class="padded_content flex_grow flex column">
	<h3>Hardware setup</h3>
	<span>In this step, you'll choose which drive to install on.<br><b><u>Important to note</u></b> is that once the "Start formatting" button is pressed, the <u>format process will start immediately</u>.<br>You can safely change drive without risk of formatting tho.</span>
	<select id="drives" class="flex_grow" size="3">
		
	</select>
	<div class="drive_information">

	</div>

	<div class="buttons bottom">
		<button id="start_format">Start formatting</button>
	</div>
</div>
"""

## TODO:
## Needs to be loaded this way, since we can't inject JS into divs etc in the HTML above.
javascript = """
window.drives_dropdown = document.querySelector('#drives');

window.refresh_drives = () => {
	window.drives_dropdown.innerHTML = '';
	Object.keys(drives).forEach((drive) => {
		let option = document.createElement('option');
		option.value = drive;
		option.innerHTML = `${drive} (${drives[drive]['size']}, ${drives[drive]['fileformats']}, ${drives[drive]['labels']})`;
		window.drives_dropdown.appendChild(option);
	})
}

window.drives_dropdown.addEventListener('change', function(obj) {
	selected_drive = this.value;

})

document.querySelector('#start_format').addEventListener('click', function() {
	socket.send({
		'_install_step' : 'hardware',
		'hardware' : {
			'drive' : selected_drive
		},
		'dependencies' : ['credentials']
	})
})

window.update_drives = (data) => {
	if(typeof data['drives'] !== 'undefined') {
		Object.keys(data['drives']).forEach((drive) => {
			drives[drive] = data['drives'][drive];
		})
		window.refresh_drives()
	}
}

if(typeof resource_handlers['hardware'] === 'undefined')
	resource_handlers['hardware'] = [update_drives];
else if(resource_handlers['hardware'].length == 1)
	resource_handlers['hardware'].push(update_drives)

socket.send({
	'_install_step' : 'hardware',
	'hardware' : 'refresh'
})

"""
def notify_partitioning_done(worker, *args, **kwargs):
	sockets[worker.client.socket.fileno()].send({
		'type' : 'notification',
		'source' : 'hardware',
		'message' : 'Paritioning is done',
		'status' : 'done'
	})

class parser():
	def parse(path, client, data, headers, fileno, addr, *args, **kwargs):
		if '_install_step' in data and data['_install_step'] == 'hardware':
			if not 'hardware' in data:
				archinstall.update_drive_list() # Updates the variable archinstall.harddrives
				print('Returning drivces')
				yield {
					'html' : html,
					'javascript' : javascript
				}
			elif 'hardware' in data and data['hardware'] == 'refresh':
				yield {
					'drives' : archinstall.harddrives
				}
			else:
				print('ONCE?')
				if 'dependencies' in data:
					for dependency in data['dependencies']:
						if not dependency in storage:
							yield {
								'status' : 'failed',
								'message' : f"Dependency '{dependency}' is not met."
							}
							return None # Break

				storage['drive'] = data['hardware']['drive']
				storage['start'] = '512MiB'
				storage['size'] = '100%'

				archinstall.args['drive'] = storage['drive']
				archinstall.args['start'] = storage['start']
				archinstall.args['size'] = storage['size']
				
				print(json.dumps(archinstall.args, indent=4))
				progress['formatting'] = True

				if not storage['SAFETY_LOCK']:
					archinstall.cache_diskpw_on_disk()
					archinstall.close_disks()
					fmt = spawn(client, archinstall.format_disk, drive='drive', start='start', end='size')
					refresh = spawn(client, archinstall.refresh_partition_list, drive='drive', dependency=fmt)
					mkfs = spawn(client, archinstall.mkfs_fat32, drive='drive', partition='1', dependency=refresh)
					encrypt = spawn(client, archinstall.encrypt_partition, drive='drive', partition='2', keyfile='pwfile', dependency=mkfs)
					mount_luksdev = spawn(client, archinstall.mount_luktsdev, drive='drive', partition='2', keyfile='pwfile', dependency=encrypt)
					btrfs = spawn(client, archinstall.mkfs_btrfs, dependency=mount_luksdev)
					mount = spawn(client, archinstall.mount_mountpoints, drive='drive', bootpartition='1', callback=notify_partitioning_done, dependency=btrfs)

				else:
					print('Emulating: Formatting drive:', storage['drive'])

				yield {
					'status' : 'success',
					'next' : 'mirrors'
				}
import json
from os.path import isdir, isfile

html = """
<div class="padded_content flex_grow flex column">
	<h3>Hardware setup</h3>
	<span>In this step, you'll choose which drive to install on.<br><b><u>Important to note</u></b> is that once the "Start formatting" button is pressed, the <u>format process will start immediately</u>.<br>You can safely change drive without risk of formatting tho.</span>
	<select id="drives">
		
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

Object.keys(drives).forEach((drive) => {
	let option = document.createElement('option');
	option.value = drive;
	option.innerHTML = `${drive} (${drives[drive]['size']}, ${drives[drive]['fileformat']})`;
	window.drives_dropdown.appendChild(option);
})

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

"""

class parser():
	def parse(path, client, data, headers, fileno, addr, *args, **kwargs):
		print(args, kwargs)
		if '_install_step' in data and data['_install_step'] == 'hardware':
			if not 'hardware' in data:
				archinstall.update_drive_list() # Updates the variable archinstall.harddrives
				yield {
					'html' : html,
					'javascript' : javascript,
					'drives' : archinstall.harddrives
				}
			else:
				if 'dependencies' in data:
					for dependency in data['dependencies']:
						if not dependency in storage:
							yield {
								'status' : 'failed',
								'message' : f"Dependency '{dependency}' is not met."
							}
							return None # Break

				storage['drive'] = data['hardware']['drive']
				print(archinstall)

				progress['formatting'] = True

				print('Yielding')
				yield {
					'status' : 'success',
					'next' : 'mirrors'
				}
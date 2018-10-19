from src.mattermostnotifier import MattermostNotifier
import digitalocean

class DropletUtils():
    def __init__(self, do_token, mattermost_webhook_url):
        self.manager = digitalocean.Manager(token=do_token)
        self.all_droplets = self.manager.get_all_droplets()
        self.notifier = MattermostNotifier(mattermost_webhook_url)

    def get_manager(self):
        return self.manager

    def get_droplet_from_id(self, droplet_id):
        droplet = self.manager.get_droplet(droplet_id)
        return droplet

    def get_all_droplets(self):
        return self.all_droplets

    def get_all_droplet_ids(self):
        droplets = self.get_all_droplets()
        droplet_ids = []
        for droplet in droplets:
            droplet_ids.append(droplet.id)
        return droplet_ids

    def create_snapshot_of_droplet(self, droplet_id):
        droplet = self.manager.get_droplet(droplet_id)
        print(f'Creating snapshot for {droplet.name} ({droplet.id})')
        try:
            droplet.take_snapshot(droplet.name)
            print(f'Snapshot for {droplet.name} ({droplet.id}) started')
            return True
        except:
            print(f'Snapshot for {droplet.name} ({droplet.id}) failed')
            return False

    def create_snapshot_of_droplets(self, droplets):
        droplet_statusses = []
        for droplet in droplets:
            snapshot_success = self.create_snapshot_of_droplet(droplet.id)
            droplet_identifier = f'{droplet.name} ({droplet.id})'
            droplet_status = {
                'identifier': droplet_identifier, 'status': snapshot_success
            }
            droplet_statusses.append(droplet_status)
        self.notify_statusses(droplet_statusses)

    def notify_statusses(self, droplet_statusses):
        notification_message = ''
        notification_message += 'Snapshot report:'
        notification_message += '\n\n'
        notification_message += '| Droplet name (id) | Status |\n'
        notification_message += '| ----------------- | ------ |\n'
        for droplet in droplet_statusses:
            new_row = f"| {droplet['identifier']} | {droplet['status']} |\n"
            notification_message += new_row
        self.notifier.send_mattermost_notification(notification_message)
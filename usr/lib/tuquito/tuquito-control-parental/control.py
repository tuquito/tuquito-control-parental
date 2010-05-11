#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 Tuquito Control Parental 0.1
 Copyright (C) 2010
 Author: Mario Colque <mario@tuquito.org.ar>
 Tuquito Team! - www.tuquito.org.ar

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; version 3 of the License.
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
"""

import gtk, pygtk
pygtk.require('2.0')
import gettext, os, time

# i18n
gettext.install('tuquito-control-parental', '/usr/share/tuquito/locale')

#-Variables
user = os.environ.get('SUDO_USER')
hosts = '/etc/hosts'
hostsTmp = '/usr/lib/tuquito/tuquito-control-parental/control.tcp'
userHome = '/home/' + user + '/TCP'

class ControlP:
	def __init__(self):
		self.glade = gtk.Builder()
		self.glade.add_from_file('/usr/lib/tuquito/tuquito-control-parental/control.glade')
		self.window = self.glade.get_object('window')
		self.window.set_title(_('Tuquito Control Parental'))
		self.glade.get_object('toolbutton_import').set_label(_('Importar lista'))
		self.glade.get_object('toolbutton_export').set_label(_('Exportar lista'))
		self.treeview_domains = self.glade.get_object('treeview_domains')

		self.column1 = gtk.TreeViewColumn(_('Dominios Bloqueados'), gtk.CellRendererText(), text=0)
		self.column1.set_sort_column_id(0)
		self.column1.set_resizable(True)
		self.treeview_domains.append_column(self.column1)
		self.treeview_domains.set_headers_clickable(True)
		self.treeview_domains.set_reorderable(False)
		self.treeview_domains.show()

		self.model = gtk.TreeStore(str)
		self.model.set_sort_column_id( 0, gtk.SORT_ASCENDING )
		self.treeview_domains.set_model(self.model)

		fontsFile = open(hostsTmp)
		for line in fontsFile:
			line = str.strip(line)
			iter = self.model.insert_before(None, None)
			self.model.set_value(iter, 0, line)
		del self.model

		self.glade.connect_signals(self)
		self.window.show()

	def notify(self, text):
		sh = 'su ' + user + ' -c "notify-send \'Tuquito Control Parental\' \'' + text + '\' -i /usr/lib/tuquito/tuquito-control-parental/control.png"'
		os.system(sh)

	def about(self, widget, data=None):
		os.system('/usr/lib/tuquito/tuquito-control-parental/control-about.py &')

	def addDomain(self, widget):
		self.glade.get_object('domain').set_text('')
		self.glade.get_object('addDomain').set_title(_('Agregar dominio'))
		self.glade.get_object('ldomain').set_label(_('Dominio: '))
		self.glade.get_object('addDomain').show()

	def closeDomain(self, widget, data=None):
		self.glade.get_object('addDomain').hide()
		return True

	def saveDomain(self, widget, data=None):
		if data != None:
			dom = data
		else:
			dom = self.glade.get_object('domain').get_text().strip().lower()
			if dom != '':
				parts = dom.split('.')
				if parts[0] == 'www':
					dom = dom + '  ' + '.'.join(parts[1:])
				else:
					dom = 'www.' + dom + '  ' + '.'.join(parts)
		domain = '0.0.0.0    ' + dom + '    # bloqueado por Tuquito 4'
		self.model = self.treeview_domains.get_model()
		iter = self.model.insert_before(None, None)
		self.model.set_value(iter, 0, dom)
		os.system('echo "' + dom + '" >> ' + hostsTmp)
		os.system('echo "' + domain + '" >> ' + hosts)
		self.closeDomain(self)

	def removeDomain(self, widget):
		self.selection = self.treeview_domains.get_selection()
		(self.model, iter) = self.selection.get_selected()
		if (iter != None):
			domain = self.model.get_value(iter, 0)
			os.system("sed '/" + domain + "/ d' " + hostsTmp + ' > ' + hostsTmp + '.back')
			os.system('mv ' + hostsTmp + '.back ' + hostsTmp)
			os.system("sed '/" + domain + "/ d' " + hosts + ' > ' + hosts + '.back.tcp')
			os.system('mv ' + hosts + '.back.tcp ' + hosts)
			self.model.remove(iter)

	def importList(self, widget):
		self.glade.get_object('filechooserdialog').set_title(_('Importar lista'))
		self.glade.get_object('filechooserdialog').show()
		self.glade.get_object('filechooserdialog').set_action(gtk.FILE_CHOOSER_ACTION_SAVE)

	def importOk(self, widget, data=None):
		importFile = self.glade.get_object('filechooserdialog').get_filename().strip()
		f = importFile.split('/')
		f = f[-1].strip().split('.')
		if len(f) == 2 and f[-1] == 'tcp':
			f = open(importFile, 'r')
			g = f.readlines()
			f.close()
			for stri in g:
				self.saveDomain(self, stri.strip())
			self.importClose(self)

	def importClose(self, widget, data=None):
		self.glade.get_object('filechooserdialog').hide()
		return True

	def exportList(self,widget):
		if not os.path.exists(userHome):
			os.mkdir(userHome)
		os.system('cp ' + hostsTmp + ' ' + userHome + '/' + time.strftime('%d-%m-%y-%H%M%S') + '.tcp')
		os.system('chmod -Rf 777 ' + userHome)
		self.notify(_('Lista de dominios exportada en\n') + userHome)

	def quit(self, widget, data=None):
		gtk.main_quit()
		return True

if __name__ == '__main__':
	if not os.path.exists('/etc/hosts.tcp.backup'):
		os.system('cp /etc/hosts /etc/hosts.tcp.backup')
	ControlP()
	gtk.main()

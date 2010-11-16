#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 Tuquito Control Parental 0.3
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

import gtk
import gettext, os, time

# i18n
gettext.install('tuquito-control-parental', '/usr/share/tuquito/locale')

#-Variables
user = os.environ.get('SUDO_USER')
hosts = '/etc/hosts'
hosts_tmp = '/usr/lib/tuquito/tuquito-control-parental/control.tcp'

class ControlP:
    def __init__(self):
        self.glade = gtk.Builder()
        self.glade.add_from_file('/usr/lib/tuquito/tuquito-control-parental/control-parental.glade')
        self.window = self.glade.get_object('window')
        self.window.set_title(_('Parental Control'))
        self.glade.get_object('toolbutton_import').set_label(_('Import list'))
        self.glade.get_object('toolbutton_export').set_label(_('Export list'))
        self.treeview_domains = self.glade.get_object('treeview_domains')

        self.column1 = gtk.TreeViewColumn(_('Blocked domains'), gtk.CellRendererText(), text=0)
        self.column1.set_sort_column_id(0)
        self.column1.set_resizable(True)
        self.treeview_domains.append_column(self.column1)
        self.treeview_domains.set_headers_clickable(True)
        self.treeview_domains.set_reorderable(False)
        self.treeview_domains.show()

        self.model = gtk.TreeStore(str)
        self.model.set_sort_column_id( 0, gtk.SORT_ASCENDING )
        self.treeview_domains.set_model(self.model)

        fonts_file = open(hosts_tmp)
        for line in fonts_file:
            line = str.strip(line)
            iter = self.model.insert_before(None, None)
            self.model.set_value(iter, 0, line)
        del self.model

        self.glade.connect_signals(self)
        self.window.show()

    def about(self, widget, data=None):
        self.glade.get_object('about').set_comments(_('Access control to websites for Tuquito.'))
        self.glade.get_object('about').show()

    def close_about(self, widget, data=None):
        self.glade.get_object('about').hide()
        return True

    def add_domain(self, widget):
        self.glade.get_object('domain').set_text('')
        self.glade.get_object('addDomain').set_title(_('Add domain'))
        self.glade.get_object('ldomain').set_label(_('Domain: '))
        self.glade.get_object('addDomain').show()

    def close_domain(self, widget, data=None):
        self.glade.get_object('addDomain').hide()
        return True

    def save_domain(self, widget, data=None):
        if data != None:
            dom = data
        else:
            dom = self.glade.get_object('domain').get_text().strip().lower()
            if dom != '':
                parts = dom.split('.')
                if parts[0] == 'www':
                    dom = dom + ' ' + '.'.join(parts[1:])
                else:
                    dom = 'www.' + dom + ' ' + '.'.join(parts)
        domain = '0.0.0.0\t' + dom + '\t#' + _('blocked by Tuquito')
        self.model = self.treeview_domains.get_model()
        iter = self.model.insert_before(None, None)
        self.model.set_value(iter, 0, dom)
        os.system('echo "' + dom + '" >> ' + hosts_tmp)
        os.system('echo "' + domain + '" >> ' + hosts)
        self.close_domain(self)

    def remove_domain(self, widget):
        self.selection = self.treeview_domains.get_selection()
        (self.model, iter) = self.selection.get_selected()
        if iter != None:
            domain = self.model.get_value(iter, 0)
            os.system("sed '/" + domain + "/ d' " + hosts_tmp + ' > ' + hosts_tmp + '.back')
            os.system('mv ' + hosts_tmp + '.back ' + hosts_tmp)
            os.system("sed '/" + domain + "/ d' " + hosts + ' > ' + hosts + '.back.tcp')
            os.system('mv ' + hosts + '.back.tcp ' + hosts)
            self.model.remove(iter)

    def import_list(self, widget):
        self.glade.get_object('filechooserdialog').set_title(_('Import list'))
        self.glade.get_object('filechooserdialog').set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        self.glade.get_object('filechooserdialog').show_all()

    def on_import_ok(self, widget, data=None):
        import_file = self.glade.get_object('filechooserdialog').get_filename().strip()
        f = import_file.split('/')
        f = f[-1].strip().split('.')
        if len(f) == 2 and f[-1] == 'tcp':
            f = open(import_file, 'r')
            g = f.readlines()
            f.close()
            for stri in g:
                self.save_domain(self, stri.strip())
            self.import_close(self)

    def import_close(self, widget, data=None):
        self.glade.get_object('filechooserdialog').hide()
        return True

    def export_list(self,widget):
        self.glade.get_object('filechooserdialog1').set_title(_('Export list'))
        self.glade.get_object('filechooserdialog1').set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        self.glade.get_object('filechooserdialog1').show_all()

    def on_export_ok(self, widget, data=None):
        try:
            export_file = self.glade.get_object('filechooserdialog1').get_filename().strip()
        except:
            print 'No hay dominios'
        else:
            sh = 'su ' + user + ' -c "cp %s %s"' % (hosts_tmp, export_file + '.tcp')
            os.system(sh)
            self.export_close(self)

    def export_close(self, widget, data=None):
        self.glade.get_object('filechooserdialog1').hide()
        return True

    def quit(self, widget, data=None):
        gtk.main_quit()
        return True

if __name__ == '__main__':
    if not os.path.exists('/etc/hosts.tcp.backup'):
        os.system('cp /etc/hosts /etc/hosts.tcp.backup')
    ControlP()
    gtk.main()

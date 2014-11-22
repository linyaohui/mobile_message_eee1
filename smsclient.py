# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import urllib
from openerp.osv import fields, orm
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)
try:
    from SOAPpy import WSDL
except :
    _logger.warning("ERROR IMPORTING SOAPpy, if not installed, please install it:"
    " e.g.: apt-get install python-soappy")
     

class SMSClient(orm.Model):
    _name = 'sms.smsclient'
    _description = 'SMS Client'

    _columns = {
        'name': fields.char('Gateway Name', size=256, required=True),
        'url': fields.char('Gateway URL', size=256,
            required=True, help='Base url for message'),
        'property_ids': fields.one2many('sms.smsclient.parms',
            'gateway_id', 'Parameters'),
       
        'method': fields.selection([
                ('http', 'HTTP Method'),
                ('smpp', 'SMPP Method')
            ], 'API Method', select=True),


        'body': fields.text('Message',
            help="The message text that will be send along with the email which is send through this server"),
   
    }

    _defaults = {

        'method': 'http',

    }


    def _prepare_smsclient_queue(self, cr, uid, data, name, context=None):
        return {
            'name': name,
            'gateway_id': data.gateway.id,

            'mobile': data.mobile_to,
            'content': data.text,
           
        }

    def _send_message(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        gateway = data.gateway
        if gateway:

            url = gateway.url
            name = url
            if gateway.method == 'http':
                prms = {}
                for p in data.gateway.property_ids:
                     if p.type == 'name':
                         prms[p.name] = p.value
                     elif p.type == 'pwd':
                         prms[p.name] = p.value
                     elif p.type == 'mobile':
                         prms[p.name] = data.mobile_to
                     elif p.type == 'content':
                         prms[p.name] = data.text
                         
                     elif p.type == 'sign':
                         prms[p.name] = p.value
                     elif p.type == 'type':
                         prms[p.name] = p.value

                     elif p.type == 'extno':
                         prms[p.name] = int(p.value)
                params = urllib.urlencode(prms)
                name = url + "?" + params
            queue_obj = self.pool.get('sms.smsclient.queue')
            vals = self._prepare_smsclient_queue(cr, uid, data, name, context=context)
            queue_obj.create(cr, uid, vals, context=context)
            f = urllib.urlopen(url, params)
            a=f.read()
        return True



class SMSQueue(orm.Model):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'

    _columns = {
        'name': fields.text('SMS Request', size=256,
            required=True, readonly=True,
           ),
        'content': fields.text('SMS Text', size=256,
            required=True, readonly=True,
           ),
        'mobile': fields.char('Mobile No', size=256,
            required=True, readonly=True,
            ),
        'gateway_id': fields.many2one('sms.smsclient',
            'SMS Gateway', readonly=True,
            ),


        'date_create': fields.datetime('Date', readonly=True),

        
    }
    _defaults = {
        'date_create': fields.datetime.now,
  
    }

class Properties(orm.Model):
    _name = 'sms.smsclient.parms'
    _description = 'SMS Client Properties'

    _columns = {
        'name': fields.char('Property name', size=256,
             help='Name of the property whom appear on the URL'),
        'value': fields.char('Property value', size=256,
             help='Value associate on the property for the URL'),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway'),
        'type': fields.selection([
                ('name', 'Name'),
                ('pwd', 'Pwd'),
                ('content', 'Content'),
                ('mobile', 'Mobile'),
                ('sign', 'SIgn'),
                ('type', 'Type'),
                ('extno', 'Extno')
            ], 'API Method', select=True,
            help='If parameter concern a value to substitute, indicate it'),
    }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

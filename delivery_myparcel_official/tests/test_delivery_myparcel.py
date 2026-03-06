# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo.tests.common import TransactionCase, Form
import unittest

from odoo.exceptions import UserError

SKIPPABLE_ERRORS = [
    'MyParcel.nl: Server not reachable',
]
SKIP_MSG = 'Test skipped due to MyParcel.nl server unavailability'


### QUESTIONS : - what is @tagged?
###             - how to run the tests?
###             - how to see the logs of the tests?
###             - Test all carriers? Destinations? Options?

class TestDeliveryMyParcel(TransactionCase):

    def setUp(self):
        super(TestDeliveryMyParcel, self).setUp()
        self.desk_chair = self.env['product.product'].create({
            'name': 'Desk Chair',
            'list_price': 42.00,
            'default_code': 'test_desk_chair',
            'weight': 1.0,
            'Volume': 0.1,
            'hs_code': '909800',
            'country_of_origin': 'NL',
        })

        self.your_company = self.env.ref('base.main_partner')
        self.your_company.write({
            'country_id': self.env.ref('base.nl').id,
            'state_id': 'Noord-Holland',
            'city': 'Hoofddorp',
            'street': 'Antareslaan 31',
            'zip': '2132 JE',
            'phone': '+31 611111111',
            'email': 'test@email.com',
        })
        self.uom_unit = self.env.ref('uom.product_uom_unit')

        ResPartner = self.env['res.partner']

        self.test_client_nl = ResPartner.create({
            'name': 'test Client (NL)',
            'country_id': self.env.ref('base.nl').id,
            'state_id': 'Zuid-Holland',
            'city': 'Den Haag',
            'street': 'Paleis Noordeinde',
            'zip': '2500 GK',
            'phone': '+31 622222222',
            'email': 'testnl@email.com',
        })
        self.test_client_be = ResPartner.create({
            'name': 'test Client (BE)',
            'country_id': self.env.ref('base.be').id,
            'state_id': 'Brussel',
            'city': 'Brussel',
            'street': 'Brederodestraat 16',
            'zip': '1000',
            'phone': '+32 633333333',
            'email': 'testbe@email.com',
        })
        self.test_client_de = ResPartner.create({
            'name': 'test Client (DE)',
            'country_id': self.env.ref('base.de').id,
            'state_id': 'Berlin',
            'city': 'Berlin',
            'street': 'Dorotheenstraße 84',
            'zip': '10117',
            'phone': '+39 644444444',
            'email': 'testde@email.com',
        })
        self.test_client_ca = ResPartner.create({
            'name': 'test Client (CA)',
            'country_id': self.env.ref('base.ca').id,
            'state_id': 'Ontario',
            'city': 'Ottawa',
            'street': '80 Wellington Street',
            'zip': 'K1A 0A2',
            'phone': '+12555555555',
            'email': 'testca@email.com',
        })

    def _get_so(self, partner_id):
        sol_vals = {
            'product_id': self.desk_chair.id,
            'name': self.desk_chair.name,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 1.0,
            'price_unit': self.desk_chair.lst_price,
        }
        so_vals = {
            'partner_id': partner_id.id,
            'order_line': [(0, None, sol_vals)],
        }

        so = self.env['sale.order'].create(so_vals)

        # make sure we use EUR
        so.pricelist_id.currency_id = self.env.ref('base.EUR')

        return so

    def _create_so(self, partner_id):
        sol_vals = {
            'product_id': self.desk_chair.id,
            'name': self.desk_chair.name,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 1.0,
            'price_unit': self.desk_chair.lst_price,
        }

        delivery_carrier = self.env['delivery.carrier'].search([
            ('delivery_type', 'like', 'myparcel_postnl'),
        ])

        so_vals = {
            'partner_id': partner_id.id,
            'order_line': [(0, None, sol_vals)],
            'carrier_id': delivery_carrier.id,
            'state': 'draft',
        }

        so = self.env['sale.order'].create(so_vals)

        # make sure we use EUR
        so.pricelist_id.currency_id = self.env.ref('base.EUR')

        return so

    def _assert_so_and_picking(self, sale_order):
        self.assertEquals(
            len(sale_order.picking_ids),
            1,
            msg='The Sales Order did not generate a picking.'
        )

        picking = sale_order.picking_ids[0]
        self.assertEquals(
            picking.carrier_id.id,
            sale_order.carrier_id.id,
            msg='Carrier is not the same on Picking and on Sale Order.'
        )

        picking.action_done()
        picking.send_to_shipper()

        self.assertIsNot(
            picking.x_aa_mp_label_url,
            False,
            msg='MyParcel did not return a label'
        )

        self.assertIsNot(
            picking.carrier_tracking_ref,
            False,
            msg='MyParcel did not return any tracking number'
        )

        label = self.env['ir.attachment'].search([
            ('res_id', '=', picking.id),
            ('res_model', '=', picking._name),
            ('description', '=', 'LabelMyParcel.pdf'),
        ])
        self.assertTrue(
            label,
            msg='MyParcel.nl label is not found in attachments'
        )

    def _get_delivery_so_wizard(
            self,
            sale_order,
            carrier_id,
            # package_type,
            # delivery_type,
            options
    ):
        try:
            form = Form(
                self.env['choose.delivery.carrier'].with_context({
                    'default_order_id': sale_order.id,
                    'default_carrier_id': carrier_id.id,
                })
            )

            # set options
            for option in options:
                setattr(form, option, options[option])


            # Do I set my options value in the with context or in the form?

            wizard = form.save()
            wizard.update_price()
            wizard.button_confirm()

            return wizard

        except UserError as e:
            if e.name.strip() in SKIPPABLE_ERRORS:
                raise unittest.SkipTest(SKIP_MSG)
            else:
                raise e





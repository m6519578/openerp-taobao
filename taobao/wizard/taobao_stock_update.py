# -*- coding: utf-8 -*-
##############################################################################
#    Taobao OpenERP Connector
#    Copyright 2012 wangbuke <wangbuke@gmail.com>
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
##############################################################################

from ..taobao_top import TOP
from osv import fields, osv

class taobao_stock_update_line(osv.osv_memory):
    _name = "taobao.stock.update.line"
    _description = "Taobao Stock Update Line"
    _columns = {
            'taobao_product_id': fields.many2one('taobao.product', 'Taobao Product'),
            'product_product_id': fields.many2one('product.product', 'Product'),
            'qty': fields.float(u'数量', required=True),
            'taobao_num_iid': fields.char(u'商品数字编码', size = 64),
            'taobao_sku_id': fields.char(u'Sku id', size = 64),
            'taobao_shop_id': fields.many2one('taobao.shop', 'Taobao Shop'),
            'update_type': fields.selection([
                (1, u'全量更新'),
                (2, u'增量更新'),
                ],
                u'库存更新方式',
                ),
            'wizard_id' : fields.many2one('taobao.stock.update', string="Wizard"),
            }

    _defaults = {
            'update_type': 1,
            }



class taobao_stock_update(osv.osv_memory):
    _name = "taobao.stock.update"
    _description = "Update Taobao Stock"
    _columns = {
            'stock_update_lines' : fields.one2many('taobao.stock.update.line', 'wizard_id', u'产品列表'),
            }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(taobao_stock_update, self).default_get(cr, uid, fields, context=context)
        active_model = context.get('active_model', False)
        active_ids = context.get('active_ids', False)

        stock_update_lines = []
        if active_model == 'taobao.product' and active_ids:
            for taobao_product_obj in self.pool.get('taobao.product').browse(cr, uid, active_ids, context=context):
                stock_update_lines.append({
                    'taobao_product_id' : taobao_product_obj.id,
                    'product_product_id' : taobao_product_obj.product_product_id.id,
                    'qty' : taobao_product_obj.product_product_id.taobao_qty_available,
                    'taobao_num_iid': taobao_product_obj.taobao_num_iid,
                    'taobao_sku_id': taobao_product_obj.taobao_sku_id,
                    'taobao_shop_id': taobao_product_obj.taobao_shop_id.id,
                    'update_type': 1,
                })

        if active_model == 'product.product' and active_ids:
            for product_product_obj in self.pool.get('product.product').browse(cr, uid, active_ids, context=context):
                for taobao_product_obj in product_product_obj.taobao_product_ids:
                    stock_update_lines.append({
                        'taobao_product_id' : taobao_product_obj.id,
                        'product_product_id' : taobao_product_obj.product_product_id.id,
                        'qty' : taobao_product_obj.product_product_id.taobao_qty_available,
                        'taobao_num_iid': taobao_product_obj.taobao_num_iid,
                        'taobao_sku_id': taobao_product_obj.taobao_sku_id,
                        'taobao_shop_id': taobao_product_obj.taobao_shop_id.id,
                        'update_type': 1,
                    })

        context['stock_update_lines'] = stock_update_lines

        if 'stock_update_lines' in fields and context.has_key('stock_update_lines'):
            res.update({'stock_update_lines': context['stock_update_lines']})

        return res


    def update_stock(self, cr, uid, ids, context=None):
        for stock_update_obj in self.browse(cr, uid, ids, context=context):
            for line in stock_update_obj.stock_update_lines:
                shop = line.taobao_shop_id
                top = TOP(shop.taobao_app_key, shop.taobao_app_secret, shop.taobao_session_key)
                self.pool.get('taobao.product')._top_item_quantity_update(top, line.qty, line.taobao_num_iid, sku_id = line.taobao_sku_id, update_type = line.update_type)

        return {
                'type': 'ir.actions.act_window_close',
                }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

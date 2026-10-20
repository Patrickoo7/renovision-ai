export default function CostTable({ estimates, onRateChange }) {
  if (!estimates?.breakdown?.length) {
    return <p className="text-center text-gray-400 py-8">No estimates yet. Set a reference dimension and calculate.</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse bg-white rounded-xl overflow-hidden shadow">
        <thead>
          <tr className="bg-[#1a1a2e] text-white text-sm">
            <th className="px-4 py-3 text-left">Region</th>
            <th className="px-4 py-3 text-left">Material</th>
            <th className="px-4 py-3 text-right">Area</th>
            <th className="px-4 py-3 text-right">Quantity</th>
            <th className="px-4 py-3 text-right">Mat Rate (₹)</th>
            <th className="px-4 py-3 text-right">Material ₹</th>
            <th className="px-4 py-3 text-right">Labor Rate (₹)</th>
            <th className="px-4 py-3 text-right">Labor ₹</th>
            <th className="px-4 py-3 text-right">Total ₹</th>
          </tr>
        </thead>
        <tbody>
          {estimates.breakdown.map((row, i) => (
            <tr key={i} className={`border-b text-sm ${i % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
              <td className="px-4 py-3 capitalize font-medium">{row.segment_label}</td>
              <td className="px-4 py-3">{row.material_name}</td>
              <td className="px-4 py-3 text-right">{row.area_sqft} {row.unit}</td>
              <td className="px-4 py-3 text-right">{row.quantity} {row.quantity_unit}</td>
              <td className="px-4 py-3 text-right">
                <input type="number" value={row.material_rate} 
                  onChange={(e) => onRateChange?.(row.segment_id, 'material_rate', parseFloat(e.target.value))}
                  className="w-20 text-right border rounded px-2 py-1 bg-white" />
              </td>
              <td className="px-4 py-3 text-right font-medium">₹{row.material_cost.toLocaleString()}</td>
              <td className="px-4 py-3 text-right">
                <input type="number" value={row.labor_rate} 
                  onChange={(e) => onRateChange?.(row.segment_id, 'labor_rate', parseFloat(e.target.value))}
                  className="w-20 text-right border rounded px-2 py-1 bg-white" />
              </td>
              <td className="px-4 py-3 text-right font-medium">₹{row.labor_cost.toLocaleString()}</td>
              <td className="px-4 py-3 text-right font-bold text-blue-700">₹{row.total_cost.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="bg-blue-50 font-bold text-sm">
            <td colSpan="5" className="px-4 py-3 text-right">TOTALS:</td>
            <td className="px-4 py-3 text-right">₹{estimates.total_material_cost.toLocaleString()}</td>
            <td></td>
            <td className="px-4 py-3 text-right">₹{estimates.total_labor_cost.toLocaleString()}</td>
            <td className="px-4 py-3 text-right text-lg text-blue-800">₹{estimates.grand_total.toLocaleString()}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  )
}

-- Preserve inline code text while allowing long paths, labels and hashes to wrap.
-- Math expressions stay math; this filter affects the PDF presentation only.
local escaped = {
  ["\\"] = "\\textbackslash{}", ["{"] = "\\{", ["}"] = "\\}",
  ["$"] = "\\$", ["%"] = "\\%", ["#"] = "\\#", ["&"] = "\\&",
  ["_"] = "\\_", ["^"] = "\\textasciicircum{}", ["~"] = "\\textasciitilde{}",
  [" "] = "\\space{}", ["≫"] = "\\ensuremath{\\gg}",
  ["ℓ"] = "\\ensuremath{\\ell}", ["∤"] = "\\ensuremath{\\nmid}",
  ["𝓔"] = "\\ensuremath{\\mathcal{E}}", ["𝒯"] = "\\ensuremath{\\mathcal{T}}",
  ["𝒰"] = "\\ensuremath{\\mathcal{U}}",
}

function Code(element)
  if not FORMAT:match("latex") then return nil end
  local output = {}
  for _, point in utf8.codes(element.text) do
    local character = utf8.char(point)
    output[#output + 1] = (escaped[character] or character) .. "\\allowbreak{}"
  end
  return pandoc.RawInline("latex", "\\texttt{" .. table.concat(output) .. "}")
end

function Str(element)
  if not FORMAT:match("latex") or not element.text:find("≫", 1, true) then return nil end
  local output = pandoc.List()
  for _, point in utf8.codes(element.text) do
    local character = utf8.char(point)
    if character == "≫" then
      output:insert(pandoc.RawInline("latex", "\\ensuremath{\\gg}"))
    else
      output:insert(pandoc.Str(character))
    end
  end
  return output
end

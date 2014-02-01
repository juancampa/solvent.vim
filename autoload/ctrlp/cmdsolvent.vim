" Solvent.vim extension for ctrlp.vim.
" Some of the code is based on the code of the 
" plugins at github.com/sgur/ctrlp-extensions.vim

let g:loaded_ctrlp_cmdsolvent = 1

" The main variable for this extension.
"
" The values are:
" + the name of the input function (including the brackets and any argument)
" + the name of the action function (only the name)
" + the long and short names to use for the statusline
" + the matching type: line, path, tabs, tabe
"                      |     |     |     |
"                      |     |     |     `- match last tab delimited str
"                      |     |     `- match first tab delimited str
"                      |     `- match full line like file/dir path
"                      `- match full line
let s:cmdsolvent_var = {
	\ 'init': 'ctrlp#cmdsolvent#init()',
	\ 'accept': 'ctrlp#cmdsolvent#accept',
	\ 'lname': 'cmdsolvent',
	\ 'sname': 'cmds',
	\ 'type': 'tabs',
	\ 'sort': 0,
	\ }


" Pre-load the vim commands list
let s:cmdsolvent_commands = []

" Append s:cmdsolvent_var to g:ctrlp_ext_vars
if exists('g:ctrlp_ext_vars') && !empty(g:ctrlp_ext_vars)
	let g:ctrlp_ext_vars = add(g:ctrlp_ext_vars, s:cmdsolvent_var)
else
	let g:ctrlp_ext_vars = [s:cmdsolvent_var]
endif


" This will be called by ctrlp to get the full list of elements
" where to look for matches
function! ctrlp#cmdsolvent#init()
  return pyeval('Solvent.GetCtrlPFileList()')
endfunction


" This will be called by ctrlp when a match is selected by the user
" Arguments:
"  a:mode   the mode that has been chosen by pressing <cr> <c-v> <c-t> or <c-x>
"           the values are 'e', 'v', 't' and 'h', respectively
"  a:str    the selected string
func! ctrlp#cmdsolvent#accept(mode, str)
  call ctrlp#exit()
  call feedkeys(':')
  call feedkeys(split(a:str, '\t')[0])
endfunc


" Give the extension an ID
let s:id = g:ctrlp_builtins + len(g:ctrlp_ext_vars)
" Allow it to be called later
function! ctrlp#cmdsolvent#id()
  return s:id
endfunction

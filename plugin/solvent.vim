" Solvent. Work with Visual Studio solutions and projects from Vim

let s:plugin_dir=expand("<sfile>:p:h")
command! Dissolve call SolventDissolve()

" Add ctrlp integration for searching within the solution
if exists('g:loaded_ctrlp') && g:loaded_ctrlp
    command! CtrlPCmdSolvent call ctrlp#init(ctrlp#cmdsolvent#id())
endif

" TODO: move this to an autoload?
function! SolventDissolve()
    " Before calling the python script set the __filename__ which for some
    " reason is not set automatically by vim.
    let g:python_filename = s:plugin_dir . '/solvent.py'
    execute "pyfile ".escape(g:python_filename, '\\')
endfunction

command! SolventBuild py Solvent.Build()
command! SolventClean py Solvent.Clean()


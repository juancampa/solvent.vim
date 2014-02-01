" Solvent.vim work with Visual Studio solutions and projects from Vim

let s:plugin_dir=expand("<sfile>:p:h")
command! Dissolve execute 'pyfile ' . s:plugin_dir . '/solvent.py'

" Add ctrlp integration for searching within the solution
if exists('g:loaded_ctrlp') && g:loaded_ctrlp
    command! CtrlPCmdSolvent call ctrlp#init(ctrlp#cmdsolvent#id())
endif


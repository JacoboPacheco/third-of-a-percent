0000000000001220 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rdx),%r8
    1223:	mov    0x8(%rdx),%r9
    1227:	sub    %r8,%r9
    122a:	je     12b4 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x94>
    1230:	sar    $0x2,%r9
    1234:	mov    (%rsi),%rax
    1237:	mov    (%rdi),%rdx
    123a:	mov    %r9d,%ecx
    123d:	and    $0x3,%ecx
    1240:	cmp    $0x4,%r9
    1244:	jae    124a <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x2a>
    1246:	xor    %esi,%esi
    1248:	jmp    1287 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x67>
    124a:	and    $0xfffffffffffffffc,%r9
    124e:	xor    %esi,%esi
    1250:	movslq (%r8,%rsi,4),%rdi
    1254:	mov    (%rax,%rdi,4),%edi
    1257:	mov    %edi,(%rdx,%rsi,4)
    125a:	movslq 0x4(%r8,%rsi,4),%rdi
    125f:	mov    (%rax,%rdi,4),%edi
    1262:	mov    %edi,0x4(%rdx,%rsi,4)
    1266:	movslq 0x8(%r8,%rsi,4),%rdi
    126b:	mov    (%rax,%rdi,4),%edi
    126e:	mov    %edi,0x8(%rdx,%rsi,4)
    1272:	movslq 0xc(%r8,%rsi,4),%rdi
    1277:	mov    (%rax,%rdi,4),%edi
    127a:	mov    %edi,0xc(%rdx,%rsi,4)
    127e:	add    $0x4,%rsi
    1282:	cmp    %rsi,%r9
    1285:	jne    1250 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x30>
    1287:	test   %rcx,%rcx
    128a:	je     12b4 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x94>
    128c:	lea    (%rdx,%rsi,4),%rdx
    1290:	lea    (%r8,%rsi,4),%rsi
    1294:	xor    %edi,%edi
    1296:	cs nopw 0x0(%rax,%rax,1)
    12a0:	movslq (%rsi,%rdi,4),%r8
    12a4:	mov    (%rax,%r8,4),%r8d
    12a8:	mov    %r8d,(%rdx,%rdi,4)
    12ac:	inc    %rdi
    12af:	cmp    %rdi,%rcx
    12b2:	jne    12a0 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    12b4:	ret
    12b5:	data16 cs nopw 0x0(%rax,%rax,1)

0000000000001240 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rdx),%rcx
    1243:	mov    0x8(%rdx),%r8
    1247:	sub    %rcx,%r8
    124a:	je     1354 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x114>
    1250:	sar    $0x2,%r8
    1254:	mov    (%rsi),%rax
    1257:	mov    (%rdi),%rsi
    125a:	cmp    $0x1,%r8
    125e:	mov    %r8,%rdi
    1261:	adc    $0x0,%rdi
    1265:	mov    %edi,%edx
    1267:	and    $0x7,%edx
    126a:	cmp    $0x8,%r8
    126e:	jae    1278 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x38>
    1270:	xor    %r8d,%r8d
    1273:	jmp    12f7 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xb7>
    1278:	and    $0xfffffffffffffff8,%rdi
    127c:	xor    %r8d,%r8d
    127f:	nop
    1280:	movslq (%rcx,%r8,4),%r9
    1284:	mov    (%rax,%r9,4),%r9d
    1288:	mov    %r9d,(%rsi,%r8,4)
    128c:	movslq 0x4(%rcx,%r8,4),%r9
    1291:	mov    (%rax,%r9,4),%r9d
    1295:	mov    %r9d,0x4(%rsi,%r8,4)
    129a:	movslq 0x8(%rcx,%r8,4),%r9
    129f:	mov    (%rax,%r9,4),%r9d
    12a3:	mov    %r9d,0x8(%rsi,%r8,4)
    12a8:	movslq 0xc(%rcx,%r8,4),%r9
    12ad:	mov    (%rax,%r9,4),%r9d
    12b1:	mov    %r9d,0xc(%rsi,%r8,4)
    12b6:	movslq 0x10(%rcx,%r8,4),%r9
    12bb:	mov    (%rax,%r9,4),%r9d
    12bf:	mov    %r9d,0x10(%rsi,%r8,4)
    12c4:	movslq 0x14(%rcx,%r8,4),%r9
    12c9:	mov    (%rax,%r9,4),%r9d
    12cd:	mov    %r9d,0x14(%rsi,%r8,4)
    12d2:	movslq 0x18(%rcx,%r8,4),%r9
    12d7:	mov    (%rax,%r9,4),%r9d
    12db:	mov    %r9d,0x18(%rsi,%r8,4)
    12e0:	movslq 0x1c(%rcx,%r8,4),%r9
    12e5:	mov    (%rax,%r9,4),%r9d
    12e9:	mov    %r9d,0x1c(%rsi,%r8,4)
    12ee:	add    $0x8,%r8
    12f2:	cmp    %r8,%rdi
    12f5:	jne    1280 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    12f7:	test   %rdx,%rdx
    12fa:	je     1354 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x114>
    12fc:	lea    (%rsi,%r8,4),%rsi
    1300:	lea    (%rcx,%r8,4),%rcx
    1304:	xor    %edi,%edi
    1306:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1315:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1324:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1333:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1340:	movslq (%rcx,%rdi,4),%r8
    1344:	mov    (%rax,%r8,4),%r8d
    1348:	mov    %r8d,(%rsi,%rdi,4)
    134c:	inc    %rdi
    134f:	cmp    %rdi,%rdx
    1352:	jne    1340 <_Z15kern_k06_gatherRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x100>
    1354:	ret
    1355:	data16 cs nopw 0x0(%rax,%rax,1)

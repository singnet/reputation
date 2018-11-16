// Code generated - DO NOT EDIT.
// This file is a generated binding and any manual changes will be lost.

package mpe

import (
	"math/big"
	"strings"

	ethereum "github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/event"
)

// Reference imports to suppress errors if they are not otherwise used.
var (
	_ = big.NewInt
	_ = strings.NewReader
	_ = ethereum.NotFound
	_ = abi.U256
	_ = bind.Bind
	_ = common.Big1
	_ = types.BloomLookup
	_ = event.NewSubscription
)

// MpeABI is the input ABI used to generate the binding from.
const MpeABI = "[{\"constant\":true,\"inputs\":[{\"name\":\"\",\"type\":\"address\"}],\"name\":\"balances\",\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[{\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"channels\",\"outputs\":[{\"name\":\"sender\",\"type\":\"address\"},{\"name\":\"recipient\",\"type\":\"address\"},{\"name\":\"groupId\",\"type\":\"bytes32\"},{\"name\":\"value\",\"type\":\"uint256\"},{\"name\":\"nonce\",\"type\":\"uint256\"},{\"name\":\"expiration\",\"type\":\"uint256\"},{\"name\":\"signer\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"nextChannelId\",\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"token\",\"outputs\":[{\"name\":\"\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"name\":\"_token\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":false,\"name\":\"channelId\",\"type\":\"uint256\"},{\"indexed\":true,\"name\":\"sender\",\"type\":\"address\"},{\"indexed\":true,\"name\":\"recipient\",\"type\":\"address\"},{\"indexed\":true,\"name\":\"groupId\",\"type\":\"bytes32\"},{\"indexed\":false,\"name\":\"signer\",\"type\":\"address\"},{\"indexed\":false,\"name\":\"amount\",\"type\":\"uint256\"},{\"indexed\":false,\"name\":\"expiration\",\"type\":\"uint256\"}],\"name\":\"ChannelOpen\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"name\":\"channelId\",\"type\":\"uint256\"},{\"indexed\":true,\"name\":\"recipient\",\"type\":\"address\"},{\"indexed\":false,\"name\":\"claimAmount\",\"type\":\"uint256\"},{\"indexed\":false,\"name\":\"sendBackAmount\",\"type\":\"uint256\"},{\"indexed\":false,\"name\":\"keepAmpount\",\"type\":\"uint256\"}],\"name\":\"ChannelClaim\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"name\":\"channelId\",\"type\":\"uint256\"},{\"indexed\":false,\"name\":\"claimAmount\",\"type\":\"uint256\"}],\"name\":\"ChannelSenderClaim\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"name\":\"channelId\",\"type\":\"uint256\"},{\"indexed\":false,\"name\":\"newExpiration\",\"type\":\"uint256\"}],\"name\":\"ChannelExtend\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"name\":\"channelId\",\"type\":\"uint256\"},{\"indexed\":false,\"name\":\"newFunds\",\"type\":\"uint256\"}],\"name\":\"ChannelAddFunds\",\"type\":\"event\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"name\":\"sender\",\"type\":\"address\"},{\"indexed\":true,\"name\":\"receiver\",\"type\":\"address\"},{\"indexed\":false,\"name\":\"amount\",\"type\":\"uint256\"}],\"name\":\"TransferFunds\",\"type\":\"event\"},{\"constant\":false,\"inputs\":[{\"name\":\"value\",\"type\":\"uint256\"}],\"name\":\"deposit\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"value\",\"type\":\"uint256\"}],\"name\":\"withdraw\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"receiver\",\"type\":\"address\"},{\"name\":\"value\",\"type\":\"uint256\"}],\"name\":\"transfer\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"recipient\",\"type\":\"address\"},{\"name\":\"value\",\"type\":\"uint256\"},{\"name\":\"expiration\",\"type\":\"uint256\"},{\"name\":\"groupId\",\"type\":\"bytes32\"},{\"name\":\"signer\",\"type\":\"address\"}],\"name\":\"openChannel\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"recipient\",\"type\":\"address\"},{\"name\":\"value\",\"type\":\"uint256\"},{\"name\":\"expiration\",\"type\":\"uint256\"},{\"name\":\"groupId\",\"type\":\"bytes32\"},{\"name\":\"signer\",\"type\":\"address\"}],\"name\":\"depositAndOpenChannel\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"channelIds\",\"type\":\"uint256[]\"},{\"name\":\"amounts\",\"type\":\"uint256[]\"},{\"name\":\"isSendbacks\",\"type\":\"bool[]\"},{\"name\":\"v\",\"type\":\"uint8[]\"},{\"name\":\"r\",\"type\":\"bytes32[]\"},{\"name\":\"s\",\"type\":\"bytes32[]\"}],\"name\":\"multiChannelClaim\",\"outputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"channelId\",\"type\":\"uint256\"},{\"name\":\"amount\",\"type\":\"uint256\"},{\"name\":\"v\",\"type\":\"uint8\"},{\"name\":\"r\",\"type\":\"bytes32\"},{\"name\":\"s\",\"type\":\"bytes32\"},{\"name\":\"isSendback\",\"type\":\"bool\"}],\"name\":\"channelClaim\",\"outputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"channelId\",\"type\":\"uint256\"},{\"name\":\"newExpiration\",\"type\":\"uint256\"}],\"name\":\"channelExtend\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"channelId\",\"type\":\"uint256\"},{\"name\":\"amount\",\"type\":\"uint256\"}],\"name\":\"channelAddFunds\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"channelId\",\"type\":\"uint256\"},{\"name\":\"newExpiration\",\"type\":\"uint256\"},{\"name\":\"amount\",\"type\":\"uint256\"}],\"name\":\"channelExtendAndAddFunds\",\"outputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"channelId\",\"type\":\"uint256\"}],\"name\":\"channelClaimTimeout\",\"outputs\":[],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"}]"

// Mpe is an auto generated Go binding around an Ethereum contract.
type Mpe struct {
	MpeCaller     // Read-only binding to the contract
	MpeTransactor // Write-only binding to the contract
	MpeFilterer   // Log filterer for contract events
}

// MpeCaller is an auto generated read-only Go binding around an Ethereum contract.
type MpeCaller struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// MpeTransactor is an auto generated write-only Go binding around an Ethereum contract.
type MpeTransactor struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// MpeFilterer is an auto generated log filtering Go binding around an Ethereum contract events.
type MpeFilterer struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// MpeSession is an auto generated Go binding around an Ethereum contract,
// with pre-set call and transact options.
type MpeSession struct {
	Contract     *Mpe              // Generic contract binding to set the session for
	CallOpts     bind.CallOpts     // Call options to use throughout this session
	TransactOpts bind.TransactOpts // Transaction auth options to use throughout this session
}

// MpeCallerSession is an auto generated read-only Go binding around an Ethereum contract,
// with pre-set call options.
type MpeCallerSession struct {
	Contract *MpeCaller    // Generic contract caller binding to set the session for
	CallOpts bind.CallOpts // Call options to use throughout this session
}

// MpeTransactorSession is an auto generated write-only Go binding around an Ethereum contract,
// with pre-set transact options.
type MpeTransactorSession struct {
	Contract     *MpeTransactor    // Generic contract transactor binding to set the session for
	TransactOpts bind.TransactOpts // Transaction auth options to use throughout this session
}

// MpeRaw is an auto generated low-level Go binding around an Ethereum contract.
type MpeRaw struct {
	Contract *Mpe // Generic contract binding to access the raw methods on
}

// MpeCallerRaw is an auto generated low-level read-only Go binding around an Ethereum contract.
type MpeCallerRaw struct {
	Contract *MpeCaller // Generic read-only contract binding to access the raw methods on
}

// MpeTransactorRaw is an auto generated low-level write-only Go binding around an Ethereum contract.
type MpeTransactorRaw struct {
	Contract *MpeTransactor // Generic write-only contract binding to access the raw methods on
}

// NewMpe creates a new instance of Mpe, bound to a specific deployed contract.
func NewMpe(address common.Address, backend bind.ContractBackend) (*Mpe, error) {
	contract, err := bindMpe(address, backend, backend, backend)
	if err != nil {
		return nil, err
	}
	return &Mpe{MpeCaller: MpeCaller{contract: contract}, MpeTransactor: MpeTransactor{contract: contract}, MpeFilterer: MpeFilterer{contract: contract}}, nil
}

// NewMpeCaller creates a new read-only instance of Mpe, bound to a specific deployed contract.
func NewMpeCaller(address common.Address, caller bind.ContractCaller) (*MpeCaller, error) {
	contract, err := bindMpe(address, caller, nil, nil)
	if err != nil {
		return nil, err
	}
	return &MpeCaller{contract: contract}, nil
}

// NewMpeTransactor creates a new write-only instance of Mpe, bound to a specific deployed contract.
func NewMpeTransactor(address common.Address, transactor bind.ContractTransactor) (*MpeTransactor, error) {
	contract, err := bindMpe(address, nil, transactor, nil)
	if err != nil {
		return nil, err
	}
	return &MpeTransactor{contract: contract}, nil
}

// NewMpeFilterer creates a new log filterer instance of Mpe, bound to a specific deployed contract.
func NewMpeFilterer(address common.Address, filterer bind.ContractFilterer) (*MpeFilterer, error) {
	contract, err := bindMpe(address, nil, nil, filterer)
	if err != nil {
		return nil, err
	}
	return &MpeFilterer{contract: contract}, nil
}

// bindMpe binds a generic wrapper to an already deployed contract.
func bindMpe(address common.Address, caller bind.ContractCaller, transactor bind.ContractTransactor, filterer bind.ContractFilterer) (*bind.BoundContract, error) {
	parsed, err := abi.JSON(strings.NewReader(MpeABI))
	if err != nil {
		return nil, err
	}
	return bind.NewBoundContract(address, parsed, caller, transactor, filterer), nil
}

// Call invokes the (constant) contract method with params as input values and
// sets the output to result. The result type might be a single field for simple
// returns, a slice of interfaces for anonymous returns and a struct for named
// returns.
func (_Mpe *MpeRaw) Call(opts *bind.CallOpts, result interface{}, method string, params ...interface{}) error {
	return _Mpe.Contract.MpeCaller.contract.Call(opts, result, method, params...)
}

// Transfer initiates a plain transaction to move funds to the contract, calling
// its default method if one is available.
func (_Mpe *MpeRaw) Transfer(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _Mpe.Contract.MpeTransactor.contract.Transfer(opts)
}

// Transact invokes the (paid) contract method with params as input values.
func (_Mpe *MpeRaw) Transact(opts *bind.TransactOpts, method string, params ...interface{}) (*types.Transaction, error) {
	return _Mpe.Contract.MpeTransactor.contract.Transact(opts, method, params...)
}

// Call invokes the (constant) contract method with params as input values and
// sets the output to result. The result type might be a single field for simple
// returns, a slice of interfaces for anonymous returns and a struct for named
// returns.
func (_Mpe *MpeCallerRaw) Call(opts *bind.CallOpts, result interface{}, method string, params ...interface{}) error {
	return _Mpe.Contract.contract.Call(opts, result, method, params...)
}

// Transfer initiates a plain transaction to move funds to the contract, calling
// its default method if one is available.
func (_Mpe *MpeTransactorRaw) Transfer(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _Mpe.Contract.contract.Transfer(opts)
}

// Transact invokes the (paid) contract method with params as input values.
func (_Mpe *MpeTransactorRaw) Transact(opts *bind.TransactOpts, method string, params ...interface{}) (*types.Transaction, error) {
	return _Mpe.Contract.contract.Transact(opts, method, params...)
}

// Balances is a free data retrieval call binding the contract method 0x27e235e3.
//
// Solidity: function balances( address) constant returns(uint256)
func (_Mpe *MpeCaller) Balances(opts *bind.CallOpts, arg0 common.Address) (*big.Int, error) {
	var (
		ret0 = new(*big.Int)
	)
	out := ret0
	err := _Mpe.contract.Call(opts, out, "balances", arg0)
	return *ret0, err
}

// Balances is a free data retrieval call binding the contract method 0x27e235e3.
//
// Solidity: function balances( address) constant returns(uint256)
func (_Mpe *MpeSession) Balances(arg0 common.Address) (*big.Int, error) {
	return _Mpe.Contract.Balances(&_Mpe.CallOpts, arg0)
}

// Balances is a free data retrieval call binding the contract method 0x27e235e3.
//
// Solidity: function balances( address) constant returns(uint256)
func (_Mpe *MpeCallerSession) Balances(arg0 common.Address) (*big.Int, error) {
	return _Mpe.Contract.Balances(&_Mpe.CallOpts, arg0)
}

// Channels is a free data retrieval call binding the contract method 0xe5949b5d.
//
// Solidity: function channels( uint256) constant returns(sender address, recipient address, groupId bytes32, value uint256, nonce uint256, expiration uint256, signer address)
func (_Mpe *MpeCaller) Channels(opts *bind.CallOpts, arg0 *big.Int) (struct {
	Sender     common.Address
	Recipient  common.Address
	GroupId    [32]byte
	Value      *big.Int
	Nonce      *big.Int
	Expiration *big.Int
	Signer     common.Address
}, error) {
	ret := new(struct {
		Sender     common.Address
		Recipient  common.Address
		GroupId    [32]byte
		Value      *big.Int
		Nonce      *big.Int
		Expiration *big.Int
		Signer     common.Address
	})
	out := ret
	err := _Mpe.contract.Call(opts, out, "channels", arg0)
	return *ret, err
}

// Channels is a free data retrieval call binding the contract method 0xe5949b5d.
//
// Solidity: function channels( uint256) constant returns(sender address, recipient address, groupId bytes32, value uint256, nonce uint256, expiration uint256, signer address)
func (_Mpe *MpeSession) Channels(arg0 *big.Int) (struct {
	Sender     common.Address
	Recipient  common.Address
	GroupId    [32]byte
	Value      *big.Int
	Nonce      *big.Int
	Expiration *big.Int
	Signer     common.Address
}, error) {
	return _Mpe.Contract.Channels(&_Mpe.CallOpts, arg0)
}

// Channels is a free data retrieval call binding the contract method 0xe5949b5d.
//
// Solidity: function channels( uint256) constant returns(sender address, recipient address, groupId bytes32, value uint256, nonce uint256, expiration uint256, signer address)
func (_Mpe *MpeCallerSession) Channels(arg0 *big.Int) (struct {
	Sender     common.Address
	Recipient  common.Address
	GroupId    [32]byte
	Value      *big.Int
	Nonce      *big.Int
	Expiration *big.Int
	Signer     common.Address
}, error) {
	return _Mpe.Contract.Channels(&_Mpe.CallOpts, arg0)
}

// NextChannelId is a free data retrieval call binding the contract method 0xf4606f00.
//
// Solidity: function nextChannelId() constant returns(uint256)
func (_Mpe *MpeCaller) NextChannelId(opts *bind.CallOpts) (*big.Int, error) {
	var (
		ret0 = new(*big.Int)
	)
	out := ret0
	err := _Mpe.contract.Call(opts, out, "nextChannelId")
	return *ret0, err
}

// NextChannelId is a free data retrieval call binding the contract method 0xf4606f00.
//
// Solidity: function nextChannelId() constant returns(uint256)
func (_Mpe *MpeSession) NextChannelId() (*big.Int, error) {
	return _Mpe.Contract.NextChannelId(&_Mpe.CallOpts)
}

// NextChannelId is a free data retrieval call binding the contract method 0xf4606f00.
//
// Solidity: function nextChannelId() constant returns(uint256)
func (_Mpe *MpeCallerSession) NextChannelId() (*big.Int, error) {
	return _Mpe.Contract.NextChannelId(&_Mpe.CallOpts)
}

// Token is a free data retrieval call binding the contract method 0xfc0c546a.
//
// Solidity: function token() constant returns(address)
func (_Mpe *MpeCaller) Token(opts *bind.CallOpts) (common.Address, error) {
	var (
		ret0 = new(common.Address)
	)
	out := ret0
	err := _Mpe.contract.Call(opts, out, "token")
	return *ret0, err
}

// Token is a free data retrieval call binding the contract method 0xfc0c546a.
//
// Solidity: function token() constant returns(address)
func (_Mpe *MpeSession) Token() (common.Address, error) {
	return _Mpe.Contract.Token(&_Mpe.CallOpts)
}

// Token is a free data retrieval call binding the contract method 0xfc0c546a.
//
// Solidity: function token() constant returns(address)
func (_Mpe *MpeCallerSession) Token() (common.Address, error) {
	return _Mpe.Contract.Token(&_Mpe.CallOpts)
}

// ChannelAddFunds is a paid mutator transaction binding the contract method 0xda2a5b4f.
//
// Solidity: function channelAddFunds(channelId uint256, amount uint256) returns(bool)
func (_Mpe *MpeTransactor) ChannelAddFunds(opts *bind.TransactOpts, channelId *big.Int, amount *big.Int) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "channelAddFunds", channelId, amount)
}

// ChannelAddFunds is a paid mutator transaction binding the contract method 0xda2a5b4f.
//
// Solidity: function channelAddFunds(channelId uint256, amount uint256) returns(bool)
func (_Mpe *MpeSession) ChannelAddFunds(channelId *big.Int, amount *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.ChannelAddFunds(&_Mpe.TransactOpts, channelId, amount)
}

// ChannelAddFunds is a paid mutator transaction binding the contract method 0xda2a5b4f.
//
// Solidity: function channelAddFunds(channelId uint256, amount uint256) returns(bool)
func (_Mpe *MpeTransactorSession) ChannelAddFunds(channelId *big.Int, amount *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.ChannelAddFunds(&_Mpe.TransactOpts, channelId, amount)
}

// ChannelClaim is a paid mutator transaction binding the contract method 0xc94fd867.
//
// Solidity: function channelClaim(channelId uint256, amount uint256, v uint8, r bytes32, s bytes32, isSendback bool) returns()
func (_Mpe *MpeTransactor) ChannelClaim(opts *bind.TransactOpts, channelId *big.Int, amount *big.Int, v uint8, r [32]byte, s [32]byte, isSendback bool) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "channelClaim", channelId, amount, v, r, s, isSendback)
}

// ChannelClaim is a paid mutator transaction binding the contract method 0xc94fd867.
//
// Solidity: function channelClaim(channelId uint256, amount uint256, v uint8, r bytes32, s bytes32, isSendback bool) returns()
func (_Mpe *MpeSession) ChannelClaim(channelId *big.Int, amount *big.Int, v uint8, r [32]byte, s [32]byte, isSendback bool) (*types.Transaction, error) {
	return _Mpe.Contract.ChannelClaim(&_Mpe.TransactOpts, channelId, amount, v, r, s, isSendback)
}

// ChannelClaim is a paid mutator transaction binding the contract method 0xc94fd867.
//
// Solidity: function channelClaim(channelId uint256, amount uint256, v uint8, r bytes32, s bytes32, isSendback bool) returns()
func (_Mpe *MpeTransactorSession) ChannelClaim(channelId *big.Int, amount *big.Int, v uint8, r [32]byte, s [32]byte, isSendback bool) (*types.Transaction, error) {
	return _Mpe.Contract.ChannelClaim(&_Mpe.TransactOpts, channelId, amount, v, r, s, isSendback)
}

// ChannelClaimTimeout is a paid mutator transaction binding the contract method 0xbaea65b5.
//
// Solidity: function channelClaimTimeout(channelId uint256) returns()
func (_Mpe *MpeTransactor) ChannelClaimTimeout(opts *bind.TransactOpts, channelId *big.Int) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "channelClaimTimeout", channelId)
}

// ChannelClaimTimeout is a paid mutator transaction binding the contract method 0xbaea65b5.
//
// Solidity: function channelClaimTimeout(channelId uint256) returns()
func (_Mpe *MpeSession) ChannelClaimTimeout(channelId *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.ChannelClaimTimeout(&_Mpe.TransactOpts, channelId)
}

// ChannelClaimTimeout is a paid mutator transaction binding the contract method 0xbaea65b5.
//
// Solidity: function channelClaimTimeout(channelId uint256) returns()
func (_Mpe *MpeTransactorSession) ChannelClaimTimeout(channelId *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.ChannelClaimTimeout(&_Mpe.TransactOpts, channelId)
}

// ChannelExtend is a paid mutator transaction binding the contract method 0x45059a5d.
//
// Solidity: function channelExtend(channelId uint256, newExpiration uint256) returns(bool)
func (_Mpe *MpeTransactor) ChannelExtend(opts *bind.TransactOpts, channelId *big.Int, newExpiration *big.Int) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "channelExtend", channelId, newExpiration)
}

// ChannelExtend is a paid mutator transaction binding the contract method 0x45059a5d.
//
// Solidity: function channelExtend(channelId uint256, newExpiration uint256) returns(bool)
func (_Mpe *MpeSession) ChannelExtend(channelId *big.Int, newExpiration *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.ChannelExtend(&_Mpe.TransactOpts, channelId, newExpiration)
}

// ChannelExtend is a paid mutator transaction binding the contract method 0x45059a5d.
//
// Solidity: function channelExtend(channelId uint256, newExpiration uint256) returns(bool)
func (_Mpe *MpeTransactorSession) ChannelExtend(channelId *big.Int, newExpiration *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.ChannelExtend(&_Mpe.TransactOpts, channelId, newExpiration)
}

// ChannelExtendAndAddFunds is a paid mutator transaction binding the contract method 0x0c19d0ec.
//
// Solidity: function channelExtendAndAddFunds(channelId uint256, newExpiration uint256, amount uint256) returns()
func (_Mpe *MpeTransactor) ChannelExtendAndAddFunds(opts *bind.TransactOpts, channelId *big.Int, newExpiration *big.Int, amount *big.Int) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "channelExtendAndAddFunds", channelId, newExpiration, amount)
}

// ChannelExtendAndAddFunds is a paid mutator transaction binding the contract method 0x0c19d0ec.
//
// Solidity: function channelExtendAndAddFunds(channelId uint256, newExpiration uint256, amount uint256) returns()
func (_Mpe *MpeSession) ChannelExtendAndAddFunds(channelId *big.Int, newExpiration *big.Int, amount *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.ChannelExtendAndAddFunds(&_Mpe.TransactOpts, channelId, newExpiration, amount)
}

// ChannelExtendAndAddFunds is a paid mutator transaction binding the contract method 0x0c19d0ec.
//
// Solidity: function channelExtendAndAddFunds(channelId uint256, newExpiration uint256, amount uint256) returns()
func (_Mpe *MpeTransactorSession) ChannelExtendAndAddFunds(channelId *big.Int, newExpiration *big.Int, amount *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.ChannelExtendAndAddFunds(&_Mpe.TransactOpts, channelId, newExpiration, amount)
}

// Deposit is a paid mutator transaction binding the contract method 0xb6b55f25.
//
// Solidity: function deposit(value uint256) returns(bool)
func (_Mpe *MpeTransactor) Deposit(opts *bind.TransactOpts, value *big.Int) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "deposit", value)
}

// Deposit is a paid mutator transaction binding the contract method 0xb6b55f25.
//
// Solidity: function deposit(value uint256) returns(bool)
func (_Mpe *MpeSession) Deposit(value *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.Deposit(&_Mpe.TransactOpts, value)
}

// Deposit is a paid mutator transaction binding the contract method 0xb6b55f25.
//
// Solidity: function deposit(value uint256) returns(bool)
func (_Mpe *MpeTransactorSession) Deposit(value *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.Deposit(&_Mpe.TransactOpts, value)
}

// DepositAndOpenChannel is a paid mutator transaction binding the contract method 0x2911dce7.
//
// Solidity: function depositAndOpenChannel(recipient address, value uint256, expiration uint256, groupId bytes32, signer address) returns(bool)
func (_Mpe *MpeTransactor) DepositAndOpenChannel(opts *bind.TransactOpts, recipient common.Address, value *big.Int, expiration *big.Int, groupId [32]byte, signer common.Address) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "depositAndOpenChannel", recipient, value, expiration, groupId, signer)
}

// DepositAndOpenChannel is a paid mutator transaction binding the contract method 0x2911dce7.
//
// Solidity: function depositAndOpenChannel(recipient address, value uint256, expiration uint256, groupId bytes32, signer address) returns(bool)
func (_Mpe *MpeSession) DepositAndOpenChannel(recipient common.Address, value *big.Int, expiration *big.Int, groupId [32]byte, signer common.Address) (*types.Transaction, error) {
	return _Mpe.Contract.DepositAndOpenChannel(&_Mpe.TransactOpts, recipient, value, expiration, groupId, signer)
}

// DepositAndOpenChannel is a paid mutator transaction binding the contract method 0x2911dce7.
//
// Solidity: function depositAndOpenChannel(recipient address, value uint256, expiration uint256, groupId bytes32, signer address) returns(bool)
func (_Mpe *MpeTransactorSession) DepositAndOpenChannel(recipient common.Address, value *big.Int, expiration *big.Int, groupId [32]byte, signer common.Address) (*types.Transaction, error) {
	return _Mpe.Contract.DepositAndOpenChannel(&_Mpe.TransactOpts, recipient, value, expiration, groupId, signer)
}

// MultiChannelClaim is a paid mutator transaction binding the contract method 0xd52ea81d.
//
// Solidity: function multiChannelClaim(channelIds uint256[], amounts uint256[], isSendbacks bool[], v uint8[], r bytes32[], s bytes32[]) returns()
func (_Mpe *MpeTransactor) MultiChannelClaim(opts *bind.TransactOpts, channelIds []*big.Int, amounts []*big.Int, isSendbacks []bool, v []uint8, r [][32]byte, s [][32]byte) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "multiChannelClaim", channelIds, amounts, isSendbacks, v, r, s)
}

// MultiChannelClaim is a paid mutator transaction binding the contract method 0xd52ea81d.
//
// Solidity: function multiChannelClaim(channelIds uint256[], amounts uint256[], isSendbacks bool[], v uint8[], r bytes32[], s bytes32[]) returns()
func (_Mpe *MpeSession) MultiChannelClaim(channelIds []*big.Int, amounts []*big.Int, isSendbacks []bool, v []uint8, r [][32]byte, s [][32]byte) (*types.Transaction, error) {
	return _Mpe.Contract.MultiChannelClaim(&_Mpe.TransactOpts, channelIds, amounts, isSendbacks, v, r, s)
}

// MultiChannelClaim is a paid mutator transaction binding the contract method 0xd52ea81d.
//
// Solidity: function multiChannelClaim(channelIds uint256[], amounts uint256[], isSendbacks bool[], v uint8[], r bytes32[], s bytes32[]) returns()
func (_Mpe *MpeTransactorSession) MultiChannelClaim(channelIds []*big.Int, amounts []*big.Int, isSendbacks []bool, v []uint8, r [][32]byte, s [][32]byte) (*types.Transaction, error) {
	return _Mpe.Contract.MultiChannelClaim(&_Mpe.TransactOpts, channelIds, amounts, isSendbacks, v, r, s)
}

// OpenChannel is a paid mutator transaction binding the contract method 0xeedcc380.
//
// Solidity: function openChannel(recipient address, value uint256, expiration uint256, groupId bytes32, signer address) returns(bool)
func (_Mpe *MpeTransactor) OpenChannel(opts *bind.TransactOpts, recipient common.Address, value *big.Int, expiration *big.Int, groupId [32]byte, signer common.Address) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "openChannel", recipient, value, expiration, groupId, signer)
}

// OpenChannel is a paid mutator transaction binding the contract method 0xeedcc380.
//
// Solidity: function openChannel(recipient address, value uint256, expiration uint256, groupId bytes32, signer address) returns(bool)
func (_Mpe *MpeSession) OpenChannel(recipient common.Address, value *big.Int, expiration *big.Int, groupId [32]byte, signer common.Address) (*types.Transaction, error) {
	return _Mpe.Contract.OpenChannel(&_Mpe.TransactOpts, recipient, value, expiration, groupId, signer)
}

// OpenChannel is a paid mutator transaction binding the contract method 0xeedcc380.
//
// Solidity: function openChannel(recipient address, value uint256, expiration uint256, groupId bytes32, signer address) returns(bool)
func (_Mpe *MpeTransactorSession) OpenChannel(recipient common.Address, value *big.Int, expiration *big.Int, groupId [32]byte, signer common.Address) (*types.Transaction, error) {
	return _Mpe.Contract.OpenChannel(&_Mpe.TransactOpts, recipient, value, expiration, groupId, signer)
}

// Transfer is a paid mutator transaction binding the contract method 0xa9059cbb.
//
// Solidity: function transfer(receiver address, value uint256) returns(bool)
func (_Mpe *MpeTransactor) Transfer(opts *bind.TransactOpts, receiver common.Address, value *big.Int) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "transfer", receiver, value)
}

// Transfer is a paid mutator transaction binding the contract method 0xa9059cbb.
//
// Solidity: function transfer(receiver address, value uint256) returns(bool)
func (_Mpe *MpeSession) Transfer(receiver common.Address, value *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.Transfer(&_Mpe.TransactOpts, receiver, value)
}

// Transfer is a paid mutator transaction binding the contract method 0xa9059cbb.
//
// Solidity: function transfer(receiver address, value uint256) returns(bool)
func (_Mpe *MpeTransactorSession) Transfer(receiver common.Address, value *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.Transfer(&_Mpe.TransactOpts, receiver, value)
}

// Withdraw is a paid mutator transaction binding the contract method 0x2e1a7d4d.
//
// Solidity: function withdraw(value uint256) returns(bool)
func (_Mpe *MpeTransactor) Withdraw(opts *bind.TransactOpts, value *big.Int) (*types.Transaction, error) {
	return _Mpe.contract.Transact(opts, "withdraw", value)
}

// Withdraw is a paid mutator transaction binding the contract method 0x2e1a7d4d.
//
// Solidity: function withdraw(value uint256) returns(bool)
func (_Mpe *MpeSession) Withdraw(value *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.Withdraw(&_Mpe.TransactOpts, value)
}

// Withdraw is a paid mutator transaction binding the contract method 0x2e1a7d4d.
//
// Solidity: function withdraw(value uint256) returns(bool)
func (_Mpe *MpeTransactorSession) Withdraw(value *big.Int) (*types.Transaction, error) {
	return _Mpe.Contract.Withdraw(&_Mpe.TransactOpts, value)
}

// MpeChannelAddFundsIterator is returned from FilterChannelAddFunds and is used to iterate over the raw logs and unpacked data for ChannelAddFunds events raised by the Mpe contract.
type MpeChannelAddFundsIterator struct {
	Event *MpeChannelAddFunds // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *MpeChannelAddFundsIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(MpeChannelAddFunds)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(MpeChannelAddFunds)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *MpeChannelAddFundsIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *MpeChannelAddFundsIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// MpeChannelAddFunds represents a ChannelAddFunds event raised by the Mpe contract.
type MpeChannelAddFunds struct {
	ChannelId *big.Int
	NewFunds  *big.Int
	Raw       types.Log // Blockchain specific contextual infos
}

// FilterChannelAddFunds is a free log retrieval operation binding the contract event 0xb0e2286f86435d8f98d9cf1c908b693792eb905dd03cd40d2b1d23a3e5311a40.
//
// Solidity: e ChannelAddFunds(channelId indexed uint256, newFunds uint256)
func (_Mpe *MpeFilterer) FilterChannelAddFunds(opts *bind.FilterOpts, channelId []*big.Int) (*MpeChannelAddFundsIterator, error) {

	var channelIdRule []interface{}
	for _, channelIdItem := range channelId {
		channelIdRule = append(channelIdRule, channelIdItem)
	}

	logs, sub, err := _Mpe.contract.FilterLogs(opts, "ChannelAddFunds", channelIdRule)
	if err != nil {
		return nil, err
	}
	return &MpeChannelAddFundsIterator{contract: _Mpe.contract, event: "ChannelAddFunds", logs: logs, sub: sub}, nil
}

// WatchChannelAddFunds is a free log subscription operation binding the contract event 0xb0e2286f86435d8f98d9cf1c908b693792eb905dd03cd40d2b1d23a3e5311a40.
//
// Solidity: e ChannelAddFunds(channelId indexed uint256, newFunds uint256)
func (_Mpe *MpeFilterer) WatchChannelAddFunds(opts *bind.WatchOpts, sink chan<- *MpeChannelAddFunds, channelId []*big.Int) (event.Subscription, error) {

	var channelIdRule []interface{}
	for _, channelIdItem := range channelId {
		channelIdRule = append(channelIdRule, channelIdItem)
	}

	logs, sub, err := _Mpe.contract.WatchLogs(opts, "ChannelAddFunds", channelIdRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(MpeChannelAddFunds)
				if err := _Mpe.contract.UnpackLog(event, "ChannelAddFunds", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// MpeChannelClaimIterator is returned from FilterChannelClaim and is used to iterate over the raw logs and unpacked data for ChannelClaim events raised by the Mpe contract.
type MpeChannelClaimIterator struct {
	Event *MpeChannelClaim // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *MpeChannelClaimIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(MpeChannelClaim)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(MpeChannelClaim)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *MpeChannelClaimIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *MpeChannelClaimIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// MpeChannelClaim represents a ChannelClaim event raised by the Mpe contract.
type MpeChannelClaim struct {
	ChannelId      *big.Int
	Recipient      common.Address
	ClaimAmount    *big.Int
	SendBackAmount *big.Int
	KeepAmpount    *big.Int
	Raw            types.Log // Blockchain specific contextual infos
}

// FilterChannelClaim is a free log retrieval operation binding the contract event 0xbe89dadc951b7d901eb74681dc1a36e63ab3f366404a072e8eede90e5615b83f.
//
// Solidity: e ChannelClaim(channelId indexed uint256, recipient indexed address, claimAmount uint256, sendBackAmount uint256, keepAmpount uint256)
func (_Mpe *MpeFilterer) FilterChannelClaim(opts *bind.FilterOpts, channelId []*big.Int, recipient []common.Address) (*MpeChannelClaimIterator, error) {

	var channelIdRule []interface{}
	for _, channelIdItem := range channelId {
		channelIdRule = append(channelIdRule, channelIdItem)
	}
	var recipientRule []interface{}
	for _, recipientItem := range recipient {
		recipientRule = append(recipientRule, recipientItem)
	}

	logs, sub, err := _Mpe.contract.FilterLogs(opts, "ChannelClaim", channelIdRule, recipientRule)
	if err != nil {
		return nil, err
	}
	return &MpeChannelClaimIterator{contract: _Mpe.contract, event: "ChannelClaim", logs: logs, sub: sub}, nil
}

// WatchChannelClaim is a free log subscription operation binding the contract event 0xbe89dadc951b7d901eb74681dc1a36e63ab3f366404a072e8eede90e5615b83f.
//
// Solidity: e ChannelClaim(channelId indexed uint256, recipient indexed address, claimAmount uint256, sendBackAmount uint256, keepAmpount uint256)
func (_Mpe *MpeFilterer) WatchChannelClaim(opts *bind.WatchOpts, sink chan<- *MpeChannelClaim, channelId []*big.Int, recipient []common.Address) (event.Subscription, error) {

	var channelIdRule []interface{}
	for _, channelIdItem := range channelId {
		channelIdRule = append(channelIdRule, channelIdItem)
	}
	var recipientRule []interface{}
	for _, recipientItem := range recipient {
		recipientRule = append(recipientRule, recipientItem)
	}

	logs, sub, err := _Mpe.contract.WatchLogs(opts, "ChannelClaim", channelIdRule, recipientRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(MpeChannelClaim)
				if err := _Mpe.contract.UnpackLog(event, "ChannelClaim", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// MpeChannelExtendIterator is returned from FilterChannelExtend and is used to iterate over the raw logs and unpacked data for ChannelExtend events raised by the Mpe contract.
type MpeChannelExtendIterator struct {
	Event *MpeChannelExtend // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *MpeChannelExtendIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(MpeChannelExtend)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(MpeChannelExtend)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *MpeChannelExtendIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *MpeChannelExtendIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// MpeChannelExtend represents a ChannelExtend event raised by the Mpe contract.
type MpeChannelExtend struct {
	ChannelId     *big.Int
	NewExpiration *big.Int
	Raw           types.Log // Blockchain specific contextual infos
}

// FilterChannelExtend is a free log retrieval operation binding the contract event 0xf8d4e64f6b2b3db6aaf38b319e259285a48ecd0c5bc0115c9928aba297c73420.
//
// Solidity: e ChannelExtend(channelId indexed uint256, newExpiration uint256)
func (_Mpe *MpeFilterer) FilterChannelExtend(opts *bind.FilterOpts, channelId []*big.Int) (*MpeChannelExtendIterator, error) {

	var channelIdRule []interface{}
	for _, channelIdItem := range channelId {
		channelIdRule = append(channelIdRule, channelIdItem)
	}

	logs, sub, err := _Mpe.contract.FilterLogs(opts, "ChannelExtend", channelIdRule)
	if err != nil {
		return nil, err
	}
	return &MpeChannelExtendIterator{contract: _Mpe.contract, event: "ChannelExtend", logs: logs, sub: sub}, nil
}

// WatchChannelExtend is a free log subscription operation binding the contract event 0xf8d4e64f6b2b3db6aaf38b319e259285a48ecd0c5bc0115c9928aba297c73420.
//
// Solidity: e ChannelExtend(channelId indexed uint256, newExpiration uint256)
func (_Mpe *MpeFilterer) WatchChannelExtend(opts *bind.WatchOpts, sink chan<- *MpeChannelExtend, channelId []*big.Int) (event.Subscription, error) {

	var channelIdRule []interface{}
	for _, channelIdItem := range channelId {
		channelIdRule = append(channelIdRule, channelIdItem)
	}

	logs, sub, err := _Mpe.contract.WatchLogs(opts, "ChannelExtend", channelIdRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(MpeChannelExtend)
				if err := _Mpe.contract.UnpackLog(event, "ChannelExtend", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// MpeChannelOpenIterator is returned from FilterChannelOpen and is used to iterate over the raw logs and unpacked data for ChannelOpen events raised by the Mpe contract.
type MpeChannelOpenIterator struct {
	Event *MpeChannelOpen // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *MpeChannelOpenIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(MpeChannelOpen)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(MpeChannelOpen)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *MpeChannelOpenIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *MpeChannelOpenIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// MpeChannelOpen represents a ChannelOpen event raised by the Mpe contract.
type MpeChannelOpen struct {
	ChannelId  *big.Int
	Sender     common.Address
	Recipient  common.Address
	GroupId    [32]byte
	Signer     common.Address
	Amount     *big.Int
	Expiration *big.Int
	Raw        types.Log // Blockchain specific contextual infos
}

// FilterChannelOpen is a free log retrieval operation binding the contract event 0x747506b844327a7a28a59a7c306bafc2b7b6d832d40dc3340152617dd174a372.
//
// Solidity: e ChannelOpen(channelId uint256, sender indexed address, recipient indexed address, groupId indexed bytes32, signer address, amount uint256, expiration uint256)
func (_Mpe *MpeFilterer) FilterChannelOpen(opts *bind.FilterOpts, sender []common.Address, recipient []common.Address, groupId [][32]byte) (*MpeChannelOpenIterator, error) {

	var senderRule []interface{}
	for _, senderItem := range sender {
		senderRule = append(senderRule, senderItem)
	}
	var recipientRule []interface{}
	for _, recipientItem := range recipient {
		recipientRule = append(recipientRule, recipientItem)
	}
	var groupIdRule []interface{}
	for _, groupIdItem := range groupId {
		groupIdRule = append(groupIdRule, groupIdItem)
	}

	logs, sub, err := _Mpe.contract.FilterLogs(opts, "ChannelOpen", senderRule, recipientRule, groupIdRule)
	if err != nil {
		return nil, err
	}
	return &MpeChannelOpenIterator{contract: _Mpe.contract, event: "ChannelOpen", logs: logs, sub: sub}, nil
}

// WatchChannelOpen is a free log subscription operation binding the contract event 0x747506b844327a7a28a59a7c306bafc2b7b6d832d40dc3340152617dd174a372.
//
// Solidity: e ChannelOpen(channelId uint256, sender indexed address, recipient indexed address, groupId indexed bytes32, signer address, amount uint256, expiration uint256)
func (_Mpe *MpeFilterer) WatchChannelOpen(opts *bind.WatchOpts, sink chan<- *MpeChannelOpen, sender []common.Address, recipient []common.Address, groupId [][32]byte) (event.Subscription, error) {

	var senderRule []interface{}
	for _, senderItem := range sender {
		senderRule = append(senderRule, senderItem)
	}
	var recipientRule []interface{}
	for _, recipientItem := range recipient {
		recipientRule = append(recipientRule, recipientItem)
	}
	var groupIdRule []interface{}
	for _, groupIdItem := range groupId {
		groupIdRule = append(groupIdRule, groupIdItem)
	}

	logs, sub, err := _Mpe.contract.WatchLogs(opts, "ChannelOpen", senderRule, recipientRule, groupIdRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(MpeChannelOpen)
				if err := _Mpe.contract.UnpackLog(event, "ChannelOpen", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// MpeChannelSenderClaimIterator is returned from FilterChannelSenderClaim and is used to iterate over the raw logs and unpacked data for ChannelSenderClaim events raised by the Mpe contract.
type MpeChannelSenderClaimIterator struct {
	Event *MpeChannelSenderClaim // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *MpeChannelSenderClaimIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(MpeChannelSenderClaim)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(MpeChannelSenderClaim)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *MpeChannelSenderClaimIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *MpeChannelSenderClaimIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// MpeChannelSenderClaim represents a ChannelSenderClaim event raised by the Mpe contract.
type MpeChannelSenderClaim struct {
	ChannelId   *big.Int
	ClaimAmount *big.Int
	Raw         types.Log // Blockchain specific contextual infos
}

// FilterChannelSenderClaim is a free log retrieval operation binding the contract event 0x10522b5c8770b85fe85ef3f007840ca9fc1bfa80b980dddc847e766a303f8cda.
//
// Solidity: e ChannelSenderClaim(channelId indexed uint256, claimAmount uint256)
func (_Mpe *MpeFilterer) FilterChannelSenderClaim(opts *bind.FilterOpts, channelId []*big.Int) (*MpeChannelSenderClaimIterator, error) {

	var channelIdRule []interface{}
	for _, channelIdItem := range channelId {
		channelIdRule = append(channelIdRule, channelIdItem)
	}

	logs, sub, err := _Mpe.contract.FilterLogs(opts, "ChannelSenderClaim", channelIdRule)
	if err != nil {
		return nil, err
	}
	return &MpeChannelSenderClaimIterator{contract: _Mpe.contract, event: "ChannelSenderClaim", logs: logs, sub: sub}, nil
}

// WatchChannelSenderClaim is a free log subscription operation binding the contract event 0x10522b5c8770b85fe85ef3f007840ca9fc1bfa80b980dddc847e766a303f8cda.
//
// Solidity: e ChannelSenderClaim(channelId indexed uint256, claimAmount uint256)
func (_Mpe *MpeFilterer) WatchChannelSenderClaim(opts *bind.WatchOpts, sink chan<- *MpeChannelSenderClaim, channelId []*big.Int) (event.Subscription, error) {

	var channelIdRule []interface{}
	for _, channelIdItem := range channelId {
		channelIdRule = append(channelIdRule, channelIdItem)
	}

	logs, sub, err := _Mpe.contract.WatchLogs(opts, "ChannelSenderClaim", channelIdRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(MpeChannelSenderClaim)
				if err := _Mpe.contract.UnpackLog(event, "ChannelSenderClaim", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// MpeTransferFundsIterator is returned from FilterTransferFunds and is used to iterate over the raw logs and unpacked data for TransferFunds events raised by the Mpe contract.
type MpeTransferFundsIterator struct {
	Event *MpeTransferFunds // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *MpeTransferFundsIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(MpeTransferFunds)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(MpeTransferFunds)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *MpeTransferFundsIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *MpeTransferFundsIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// MpeTransferFunds represents a TransferFunds event raised by the Mpe contract.
type MpeTransferFunds struct {
	Sender   common.Address
	Receiver common.Address
	Amount   *big.Int
	Raw      types.Log // Blockchain specific contextual infos
}

// FilterTransferFunds is a free log retrieval operation binding the contract event 0x5a0155838afb0f859197785e575b9ad1afeb456c6e522b6f632ee8465941315e.
//
// Solidity: e TransferFunds(sender indexed address, receiver indexed address, amount uint256)
func (_Mpe *MpeFilterer) FilterTransferFunds(opts *bind.FilterOpts, sender []common.Address, receiver []common.Address) (*MpeTransferFundsIterator, error) {

	var senderRule []interface{}
	for _, senderItem := range sender {
		senderRule = append(senderRule, senderItem)
	}
	var receiverRule []interface{}
	for _, receiverItem := range receiver {
		receiverRule = append(receiverRule, receiverItem)
	}

	logs, sub, err := _Mpe.contract.FilterLogs(opts, "TransferFunds", senderRule, receiverRule)
	if err != nil {
		return nil, err
	}
	return &MpeTransferFundsIterator{contract: _Mpe.contract, event: "TransferFunds", logs: logs, sub: sub}, nil
}

// WatchTransferFunds is a free log subscription operation binding the contract event 0x5a0155838afb0f859197785e575b9ad1afeb456c6e522b6f632ee8465941315e.
//
// Solidity: e TransferFunds(sender indexed address, receiver indexed address, amount uint256)
func (_Mpe *MpeFilterer) WatchTransferFunds(opts *bind.WatchOpts, sink chan<- *MpeTransferFunds, sender []common.Address, receiver []common.Address) (event.Subscription, error) {

	var senderRule []interface{}
	for _, senderItem := range sender {
		senderRule = append(senderRule, senderItem)
	}
	var receiverRule []interface{}
	for _, receiverItem := range receiver {
		receiverRule = append(receiverRule, receiverItem)
	}

	logs, sub, err := _Mpe.contract.WatchLogs(opts, "TransferFunds", senderRule, receiverRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(MpeTransferFunds)
				if err := _Mpe.contract.UnpackLog(event, "TransferFunds", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}
